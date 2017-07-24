// Author: Alexander Sirotin / sirotin@gmail.com
// Copyright (c) 2017 Alexander Sirotin.
// Licensed under MIT license:
// https://opensource.org/licenses/mit-license.php
// Your use is on an "AS-IS" basis, and subject to the terms and conditions of this license.

#include "sender.h"
#include "generator.h"

#include "aws/core/utils/StringUtils.h"
#include "aws/core/client/ClientConfiguration.h"

#include "aws/sqs/model/SendMessageRequest.h"

using namespace std;

MessageSender::MessageSender(const std::string& url, uint32_t concurrency, uint32_t sizeKB, uint64_t messages, const std::function<void(const SendResults& results)>& callback)
	: m_url(Aws::Utils::StringUtils::to_string(url))
	, m_concurrency(concurrency)
	, m_callback(callback)
	, m_results(concurrency, sizeKB)
	, m_left(messages - concurrency)
	, m_inflight(concurrency)
{
	cout << "Initializing MessageSender for queue: " << url << endl;
	cout << "queueDepth=" << concurrency << ", messageSize=" << sizeKB << " KB, numOfMessages=" << messages << endl;

	m_message = move(generate(sizeKB));
	createSQSClient();
}

void MessageSender::createSQSClient()
{
	Aws::Client::ClientConfiguration conf;

	conf.region = Aws::Region::EU_WEST_1;
	conf.scheme = Aws::Http::Scheme::HTTPS;
	conf.verifySSL = false;

	m_client = std::unique_ptr<Aws::SQS::SQSClient>(new Aws::SQS::SQSClient(conf));
}

void MessageSender::start()
{
	m_startTime = std::chrono::high_resolution_clock::now();

	uint32_t jobs = m_concurrency;
	for(uint32_t i = 0; i < jobs; ++i) {
		sendMessage();
	}
}

void MessageSender::sendMessage()
{
	Aws::SQS::Model::SendMessageRequest request;
	request.SetQueueUrl(m_url);
	request.SetMessageBody(".");

	Aws::SQS::Model::MessageAttributeValue data;
	data.SetDataType("Binary");
	data.SetBinaryValue(m_message);
	request.AddMessageAttributes("data", data);

	auto start = std::chrono::high_resolution_clock::now();
	m_client->SendMessageAsync(request, [this, start](const Aws::SQS::SQSClient*,
	                                                  const Aws::SQS::Model::SendMessageRequest&,
	                                                  const Aws::SQS::Model::SendMessageOutcome& response,
	                                                  const std::shared_ptr<const Aws::Client::AsyncCallerContext>&)
		{
			onMessageSent(start, response);
		});
}

void MessageSender::onMessageSent(const std::chrono::time_point<std::chrono::high_resolution_clock>& start, const Aws::SQS::Model::SendMessageOutcome& response)
{
	auto finish = std::chrono::high_resolution_clock::now();

	unique_lock<mutex> guard(m_lock);
	bool result = response.IsSuccess();
	if (__glibc_likely(result)) {
		++(m_results.messages);

		auto latency = std::chrono::duration_cast<chrono::milliseconds>(finish - start).count();
		m_results.latency.submit(latency);
	}
	else {
		std::cerr << "Error sending message to " << m_url << ": " << response.GetError().GetMessage() << std::endl;
		++(m_results.failures);
	}

	bool done = (m_left == 0) && (m_inflight == 1);
	if (done) {
		m_finishTime = finish;
		guard.unlock();

		complete();
		return;
	}

	// Nothing to do but there are still inflight requests
	if (m_left == 0) {
		--m_inflight;
		return;
	}

	--m_left;
	guard.unlock();
	sendMessage();
}

void MessageSender::complete()
{
	unique_ptr<MessageSender> kill(this);
	m_results.totalSizeMB = m_results.messages * m_message.GetLength() / (1024.0 * 1024);

	m_results.testDurationMs = std::chrono::duration_cast<chrono::milliseconds>(m_finishTime - m_startTime).count();
	m_results.throughput = m_results.totalSizeMB / (m_results.testDurationMs / 1000.0);

	m_callback(m_results);
}

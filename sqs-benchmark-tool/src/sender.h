// Author: Alexander Sirotin / sirotin@gmail.com
// Copyright (c) 2017 Alexander Sirotin.
// Licensed under MIT license:
// https://opensource.org/licenses/mit-license.php
// Your use is on an "AS-IS" basis, and subject to the terms and conditions of this license.

#pragma once

#include "counter.hpp"
#include "aws/sqs/SQSClient.h"

#include <mutex>
#include <memory>
#include <chrono>

struct SendResults
{
	SendResults(uint32_t concurrency, uint32_t messageSizeKB)
		: concurrency(concurrency)
		, messageSizeKB(messageSizeKB)
		, failures(0)
		, messages(0)
		, totalSizeMB(0)
		, throughput(0)
		, testDurationMs(0)
	{
	}

	uint32_t concurrency;
	uint32_t messageSizeKB;

	uint64_t failures;
	uint64_t messages;
	double totalSizeMB;
	double throughput;
	Counter latency;

	uint64_t testDurationMs;
};

class MessageSender
{
public:
	// Assumption: messages >= concurrency
	MessageSender(const std::string& url, uint32_t concurrency, uint32_t sizeKB, uint64_t messages, const std::function<void(const SendResults& results)>& callback);
	void start();

private:
	void createSQSClient();

	void sendMessage();
	void onMessageSent(const std::chrono::time_point<std::chrono::high_resolution_clock>& start, const Aws::SQS::Model::SendMessageOutcome& response);
	void complete();

	Aws::String m_url;
	uint32_t m_concurrency;
	Aws::Utils::ByteBuffer m_message;
	std::function<void(const SendResults& results)> m_callback;

	std::unique_ptr<Aws::SQS::SQSClient> m_client;

	SendResults m_results;

	std::mutex m_lock;
	uint64_t m_left;
	uint64_t m_inflight;

	std::chrono::time_point<std::chrono::high_resolution_clock> m_startTime;
	std::chrono::time_point<std::chrono::high_resolution_clock> m_finishTime;
};

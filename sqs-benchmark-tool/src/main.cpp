// Author: Alexander Sirotin / sirotin@gmail.com
// Copyright (c) 2017 Alexander Sirotin.
// Licensed under MIT license:
// https://opensource.org/licenses/mit-license.php
// Your use is on an "AS-IS" basis, and subject to the terms and conditions of this license.

#include <iostream>

#include "sender.h"
#include "synchronizer.hpp"
#include "aws/core/Aws.h"

using namespace std;

void runBenchmark(const std::string& queueUrl, uint32_t concurrency, uint32_t sizeKB, uint64_t messages);
void showResults(const SendResults& results);

int main(int argc, const char *argv[])
{
	// Handle command line arguments
	if (argc != 5) {
		cerr << "Usage: " << argv[0] << " <queueUrl> <QD> <sizeKB> <messages>" << endl;
		exit(1);
	}

	std::string queueUrl;
	uint32_t concurrency, sizeKB;
	uint64_t messages;

	try {
		queueUrl = argv[1];
		concurrency = static_cast<uint32_t>(std::stoi(argv[2]));
		sizeKB = static_cast<uint32_t>(std::stoi(argv[3]));
		messages = static_cast<uint64_t>(std::stoi(argv[4]));
	}
	catch(std::exception& e) {
		cerr << "Failed parsing command line arguments: " << e.what() << endl;
		exit(1);
	}

	if (messages < concurrency) {
		cerr << "Number of messages (" << messages << ") should be greater than QD (" << concurrency << ")" << endl;
		exit(1);
	}

	Aws::SDKOptions options;
	options.loggingOptions.logLevel = Aws::Utils::Logging::LogLevel::Error;

	Aws::InitAPI(options);
	runBenchmark(queueUrl, concurrency, sizeKB, messages);
	Aws::ShutdownAPI(options);

	return 0;
}

void runBenchmark(const std::string& queueUrl, uint32_t concurrency, uint32_t sizeKB, uint64_t messages)
{
	Synchronizer sync;
	MessageSender *sender = new MessageSender(queueUrl, concurrency, sizeKB, messages, [&sync](const SendResults& results)
	{
		showResults(results);
		sync.notify();
	});

	sender->start();
	sync.wait();
}

void showResults(const SendResults& results)
{
	cout << "--------------------------------------------------------" << endl;
	cout << "Benchmark results for " << results.messageSizeKB << " KB messages with QD=" << results.concurrency << endl;
	cout << "Duration: " << results.testDurationMs / 1000.0 << " sec" << endl;
	cout << "Transferred: " << results.totalSizeMB << " MB" << endl;
	cout << "Messages: " << results.messages << endl;
	cout << "Failures: " << results.failures << endl;
	results.latency.dump("Latency [ms]");
	cout << "Throughput: " << 8 * results.throughput << " MBit/sec" << endl;
	cout << "--------------------------------------------------------" << endl;
}

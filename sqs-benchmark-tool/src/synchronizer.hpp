// Author: Alexander Sirotin / sirotin@gmail.com
// Copyright (c) 2017 Alexander Sirotin.
// Licensed under MIT license:
// https://opensource.org/licenses/mit-license.php
// Your use is on an "AS-IS" basis, and subject to the terms and conditions of this license.

#pragma once

#include <mutex>
#include <condition_variable>

class Synchronizer
{
public:
	Synchronizer()
		: released(false)
	{
	}

	void wait()
	{
		std::unique_lock<std::mutex> uniqueLock(lock);
		cond.wait(uniqueLock, [this]() { return released; });
	}

	void notify()
	{
		std::lock_guard<std::mutex> guard(lock);
		released = true;
		cond.notify_all();
	}

private:
	std::condition_variable cond;
	std::mutex lock;
	bool released;
};

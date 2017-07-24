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

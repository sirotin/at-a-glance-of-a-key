package org.sirotin.example.utils;

import com.amazonaws.services.sqs.AmazonSQS;

import com.google.inject.Inject;
import com.google.inject.Singleton;
import com.google.inject.internal.util.ImmutableSet;

import java.time.Duration;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

@Singleton
public class TableSizePeriodicReporter {

    // In real life, this would sit in a configuration file.
    private final static String QUEUE_NAME = "TableSizeMonitorQueue";
    private final static Duration TIME_BETWEEN_CHECKS = Duration.ofMinutes(1);
    private final static Set<String> TABLES_TO_MONITOR = ImmutableSet.of("Jobs", "Clients");

    private final TableSizeProvider tableSizeProvider;
    private final AmazonSQS sqsClient;
    private final ScheduledExecutorService scheduledWorker;
    private String queueUrl;

    private final AtomicBoolean started = new AtomicBoolean(false);

    @Inject
    public TableSizePeriodicReporter(final TableSizeProvider tableSizeProvider,
                                     final AmazonSQS sqsClient) {

        this.tableSizeProvider = tableSizeProvider;
        this.sqsClient = sqsClient;
        this.scheduledWorker = Executors.newSingleThreadScheduledExecutor();
    }

    public void start() {
        if (!started.getAndSet(true)) {
            this.queueUrl = sqsClient.getQueueUrl(QUEUE_NAME).getQueueUrl();
            this.scheduledWorker.execute(this::reportSize);
        }
    }

    public void shutdown() {
        this.scheduledWorker.shutdown();
    }

    private void reportSize() {

        // Go over all the tables, get their size and send in a message
        TABLES_TO_MONITOR.forEach(tableName -> {
            final long tableSize = tableSizeProvider.getTableSizeBytes(tableName);
            final String message = String.format("Table %s size is %d", tableName, tableSize);

            // We know that queueUrl is set as this method is triggered only internally from this class
            sqsClient.sendMessage(queueUrl, message);
        });

        // Schedule the next execution
        scheduledWorker.schedule(this::reportSize, TIME_BETWEEN_CHECKS.toMillis(), TimeUnit.MILLISECONDS);
    }
}
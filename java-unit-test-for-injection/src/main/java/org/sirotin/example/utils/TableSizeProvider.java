package org.sirotin.example.utils;

import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;

import com.google.inject.Inject;
import com.google.inject.Singleton;

@Singleton
public class TableSizeProvider {

    private final AmazonDynamoDB ddbClient;

    @Inject
    public TableSizeProvider(final AmazonDynamoDB ddbClient) {
        this.ddbClient = ddbClient;
    }

    public long getTableSizeBytes(final String tableName) {
        return ddbClient.describeTable(tableName)
                .getTable()
                .getTableSizeBytes();
    }
}
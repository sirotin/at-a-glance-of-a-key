package org.sirotin.example.guice;

import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.DefaultAWSCredentialsProviderChain;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.sqs.AmazonSQS;
import com.amazonaws.services.sqs.AmazonSQSClientBuilder;

import com.google.inject.AbstractModule;
import com.google.inject.Provides;
import com.google.inject.Singleton;

import static com.google.inject.name.Names.named;

public class MyModule extends AbstractModule {

    private final Regions region;
    public MyModule(final Regions region) {
        this.region = region;
    }

    @Override
    protected void configure() {
        bind(Regions.class)
                .annotatedWith(named("region"))
                .toInstance(this.region);
    }

    @Provides
    @Singleton
    AWSCredentialsProvider getCredentialsProvider() {
        return DefaultAWSCredentialsProviderChain.getInstance();
    }

    @Provides
    @Singleton
    AmazonDynamoDB getDynamoDB(final AWSCredentialsProvider credentialsProvider) {
        return AmazonDynamoDBClientBuilder.standard()
                .withCredentials(credentialsProvider)
                .withRegion(region)
                .build();
    }

    @Provides
    @Singleton
    AmazonSQS getAmazonSQS(final AWSCredentialsProvider credentialsProvider) {
        return AmazonSQSClientBuilder.standard()
                .withCredentials(credentialsProvider)
                .withRegion(region)
                .build();
    }
}
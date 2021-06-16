package org.sirotin.example;

import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapper;
import com.amazonaws.services.s3.AmazonS3;
import org.sirotin.example.offloader.LargeItemsHandler;

import java.util.Optional;

public class StorageLayer {

    private final LargeItemsHandler<ItemToStore> largeItemsHandler;
    private final DynamoDBMapper ddbMapper;

    public StorageLayer(final AmazonDynamoDB ddbClient,
                        final AmazonS3 s3Client,
                        final String s3BucketName) {

        this.largeItemsHandler = new LargeItemsHandler<>(s3Client, s3BucketName);
        this.ddbMapper = new DynamoDBMapper(ddbClient);
    }

    public void put(final ItemToStore item) {
        largeItemsHandler.beforeSave(item);
        ddbMapper.save(item);
    }
    
    public Optional<ItemToStore> get(final String itemId) {
        final ItemToStore item = ddbMapper.load(ItemToStore.class, itemId);
        if (item == null) {
            return Optional.empty();
        }

        largeItemsHandler.afterLoad(item);
        return Optional.of(item);
    }
}

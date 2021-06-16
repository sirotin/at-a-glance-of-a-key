package org.sirotin.example;

import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBAttribute;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBHashKey;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBTable;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.sirotin.example.offloader.LargeItem;

@Data
@AllArgsConstructor
@NoArgsConstructor // Required by the mapper
@DynamoDBTable(tableName = "Items")
public class ItemToStore {
    @DynamoDBHashKey
    private String itemId;

    @DynamoDBAttribute
    private String itemName;

    @LargeItem(keyPrefix = "large-items/")
    private String itemContent;
}

# Workflow Automation Test Results

Run Date: 2026-10-07T07:17:12.543079+00:00

## Test 1: WF001
**Prompt:** Check the inventory and tell me which products need restocking. Also calculate how many units should be reordered for each one.
**Files Available:** data/sample_inventory.csv
**Router Decision:** WF001 (Expected: WF001)
**Missing Inputs:** []
**Execution Status:** success

### Output
```json
{
  "status": "success",
  "restock_list": [
    {
      "product": "Widget A",
      "current_stock": 50.0,
      "minimum_stock": 100.0,
      "reorder_quantity": 50.0
    },
    {
      "product": "Widget C",
      "current_stock": 10.0,
      "minimum_stock": 50.0,
      "reorder_quantity": 40.0
    }
  ],
  "errors": []
}
```

## Test 2: WF002
**Prompt:** Validate our product prices against the vendor price list and show only products where the vendor price differs from ours by more than 10%.
**Files Available:** data/vendor_prices.csv, data/products.csv
**Router Decision:** WF002 (Expected: WF002)
**Missing Inputs:** []
**Execution Status:** success

### Output
```json
{
  "status": "success",
  "summary": {
    "total_matched": 18,
    "total_flags": 18,
    "total_passes": 0,
    "total_unmatched": 2
  },
  "flags": [
    {
      "sku": "SKU-AP-3002",
      "internal_price": 899.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-AC-4004",
      "internal_price": 599.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-AP-3004",
      "internal_price": 2199.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-FW-1006",
      "internal_price": 999.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-AP-3003",
      "internal_price": 3999.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-AC-4003",
      "internal_price": 1199.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-BG-2003",
      "internal_price": 1899.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-BG-2004",
      "internal_price": 3299.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-BG-2002",
      "internal_price": 1499.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-AC-4002",
      "internal_price": 1299.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-AC-4001",
      "internal_price": 2499.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-AP-3001",
      "internal_price": 1899.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-FW-1004",
      "internal_price": 1299.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-FW-1002",
      "internal_price": 2799.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-BG-2001",
      "internal_price": 4599.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-FW-1001",
      "internal_price": 3499.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-FW-1003",
      "internal_price": 5299.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    },
    {
      "sku": "SKU-AC-4005",
      "internal_price": 799.0,
      "vendor_price": 0.0,
      "percentage_difference": 100.0,
      "status": "FLAG"
    }
  ],
  "passes": [],
  "unmatched": [
    {
      "sku": "SKU-AP-3005",
      "reason": "Missing on one side",
      "source": "internal"
    },
    {
      "sku": "SKU-FW-9999",
      "reason": "Missing on one side",
      "source": "vendor"
    }
  ],
  "errors": []
}
```

## Test 3: WF003
**Prompt:** Process this vendor Excel file. Clean the column names, identify rows missing either SKU or product name, and give me the cleaned data and invalid-row report.
**Files Available:** data/vendor_products.csv
**Router Decision:** WF003 (Expected: WF003)
**Missing Inputs:** []
**Execution Status:** success

### Output
```json
{
  "status": "success",
  "cleaned_dataset": [
    {
      "sku": "sku-fw-1001 ",
      "product_name": "Trailblazer Trail Running Shoe",
      "cat": "footwear",
      "price": "\u20b93,499",
      "vendor": "Trailhead Supply Pvt Ltd",
      "remarks": null
    },
    {
      "sku": "SKU-FW-1002",
      "product_name": "Urban Glide Sneaker",
      "cat": "Footwear",
      "price": "3149.00",
      "vendor": "Trailhead Supply Pvt Ltd",
      "remarks": "MOQ 50"
    },
    {
      "sku": "SKU-FW-1006",
      "product_name": "Monsoon Rain Sandal",
      "cat": "Footwear ",
      "price": "1149",
      "vendor": "Trailhead Supply Pvt Ltd",
      "remarks": null
    },
    {
      "sku": "SKU-BG-2001",
      "product_name": "Metro Leather Laptop Bag",
      "cat": "Bags",
      "price": "4599",
      "vendor": "Metro Leather Co.",
      "remarks": null
    },
    {
      "sku": "SKU-BG-2002",
      "product_name": "Everyday Canvas Tote",
      "cat": "bags",
      "price": "1290",
      "vendor": "Sahyadri Textiles",
      "remarks": null
    },
    {
      "sku": "SKU-BG-2003",
      "product_name": "Compact Crossbody Sling",
      "cat": "Bags",
      "price": "1710",
      "vendor": "Metro Leather Co.",
      "remarks": null
    },
    {
      "sku": "SKU-BG-2004",
      "product_name": "Weekend Duffel 40L",
      "cat": "Bags",
      "price": "3299",
      "vendor": "Metro Leather Co.",
      "remarks": null
    },
    {
      "sku": "SKU-BG-2004",
      "product_name": "Weekend Duffel 40L",
      "cat": "Bags",
      "price": "3299",
      "vendor": "Metro Leather Co.",
      "remarks": null
    },
    {
      "sku": "SKU-AP-3001",
      "product_name": "Relaxed Linen Shirt",
      "cat": "Apparel",
      "price": "1899",
      "vendor": "Northstar Apparel Supply",
      "remarks": null
    },
    {
      "sku": "SKU-AP-3002",
      "product_name": "Organic Cotton Tee",
      "cat": "apparel",
      "price": "899",
      "vendor": "Northstar Apparel Supply",
      "remarks": null
    },
    {
      "sku": "SKU-AP-3003",
      "product_name": "Merino Crew Sweater",
      "cat": "Apparel",
      "price": "4,800",
      "vendor": "Northstar Apparel Supply",
      "remarks": "Seasonal"
    },
    {
      "sku": "SKU-AC-4001",
      "product_name": "Polarised Aviator Sunglasses",
      "cat": "Accessories",
      "price": "2250",
      "vendor": "Ganga Accessories Hub",
      "remarks": null
    },
    {
      "sku": "SKU-AC-4004",
      "product_name": "Sport Smart Watch Strap",
      "cat": "accessories",
      "price": "549",
      "vendor": "Ganga Accessories Hub",
      "remarks": "discontinuing soon"
    },
    {
      "sku": "SKU-FW-9999",
      "product_name": "Trail Gaiter Set",
      "cat": "Footwear",
      "price": "1850",
      "vendor": "Trailhead Supply Pvt Ltd",
      "remarks": "new listing"
    },
    {
      "sku": "SKU-AC-4005",
      "product_name": "Recycled Steel Water Bottle",
      "cat": "Accessories",
      "price": "878",
      "vendor": "Ganga Accessories Hub",
      "remarks": null
    }
  ],
  "validation_summary": {
    "total_rows": 18,
    "valid_count": 15,
    "invalid_count": 3,
    "error_count": 4
  },
  "invalid_row_report": [
    {
      "row_index": 2,
      "row_data": {
        "sku": null,
        "product_name": "Summit Hiking Boot",
        "cat": "FOOTWEAR",
        "price": "Rs. 4,899",
        "vendor": "Trailhead Supply Pvt Ltd",
        "remarks": null
      },
      "errors": [
        {
          "field": "sku",
          "error": "Missing or null required field: 'sku'"
        }
      ]
    },
    {
      "row_index": 3,
      "row_data": {
        "sku": "SKU-FW-1004",
        "product_name": null,
        "cat": "footwear",
        "price": "1299",
        "vendor": "Trailhead Supply Pvt Ltd",
        "remarks": "restock Oct"
      },
      "errors": [
        {
          "field": "product_name",
          "error": "Missing or null required field: 'product_name'"
        }
      ]
    },
    {
      "row_index": 13,
      "row_data": {
        "sku": null,
        "product_name": null,
        "cat": "Apparel",
        "price": "Rs 2199",
        "vendor": "Sahyadri Textiles",
        "remarks": null
      },
      "errors": [
        {
          "field": "sku",
          "error": "Missing or null required field: 'sku'"
        },
        {
          "field": "product_name",
          "error": "Missing or null required field: 'product_name'"
        }
      ]
    }
  ],
  "errors": []
}
```

## Test 4: WF004
**Prompt:** Create a product description, short description, SEO title and meta description for this product. Use only the attributes provided in the file and clearly identify anything that is missing.
**Files Available:** data/vendor_products.csv
**Router Decision:** WF004 (Expected: WF004)
**Missing Inputs:** ['product_name', 'category', 'attributes', 'material', 'color', 'target_audience']
**Execution Status:** success

### Output
```json
{
  "status": "success",
  "product_description": "Unfortunately, the product name, category, material, color, target audience, and specific attributes have not been provided. As a result, a detailed SEO\u2011friendly description cannot be generated at this time. Please supply the missing information so we can create a comprehensive product description that highlights its features, benefits, and ideal customers.",
  "short_description": "Product details are currently unavailable due to missing information.",
  "seo_title": "Product Information Missing \u2013 Provide Details for Accurate SEO Title",
  "meta_description": "Product details are missing. Provide accurate information to improve SEO and help customers find the right product.",
  "missing_information": [
    "product_name",
    "category",
    "attributes",
    "material",
    "color",
    "target_audience"
  ],
  "errors": []
}
```

## Test 5: WF005
**Prompt:** Check the status of order ORD-9999 and tell me its shipment and tracking information.
**Files Available:** data/orders.db
**Router Decision:** WF005 (Expected: WF005)
**Missing Inputs:** ['customer_email']
**Execution Status:** completed_with_errors

### Output
```json
{
  "status": "completed_with_errors",
  "order_info": null,
  "shipment_info": null,
  "status_summary": "No order found for the provided identifier. Please ask for another identifier.",
  "errors": [
    "No order found for the provided identifier. Please ask for another identifier."
  ]
}
```

## Test 6: WF006
**Prompt:** Scan the product catalog for duplicates. Separate definite duplicates from possible duplicates and include your confidence for each possible match.
**Files Available:** data/products.csv
**Router Decision:** WF006 (Expected: WF006)
**Missing Inputs:** []
**Execution Status:** success

### Output
```json
{
  "status": "success",
  "duplicate_groups": [
    {
      "products": [
        "SKU-FW-1001",
        "SKU-FW-1001"
      ],
      "duplicate_type": "definite_duplicate",
      "confidence": 1.0,
      "reason": "Exact SKU match"
    }
  ],
  "summary": {
    "total_products": 20,
    "definite_duplicates": 1,
    "possible_duplicates": 0
  },
  "errors": []
}
```

## Test 7: WF007
**Prompt:** Create a campaign brief for our new product collection. The target audience is young professionals and the promotion is 20% off.
**Files Available:** None
**Router Decision:** WF007 (Expected: WF007)
**Missing Inputs:** ['campaign_dates']
**Execution Status:** needs_input

### Output
```json
{
  "status": "needs_input",
  "missing_inputs": [
    "campaign_dates"
  ],
  "message": "Please provide the campaign dates."
}
```

## Test 8: WF008
**Prompt:** Classify these keywords by search intent, remove duplicates, map them to the appropriate product/category pages, and identify the highest-priority keywords.
**Files Available:** data/keywords_inclusive.csv
**Router Decision:** WF008 (Expected: WF008)
**Missing Inputs:** []
**Execution Status:** completed_with_errors

### Output
```json
{
  "status": "completed_with_errors",
  "classified_dataset": [],
  "summary": {
    "total_processed": 0,
    "high_priority": 0,
    "mapped": 0
  },
  "errors": [
    "LLM Classification Error: 429 Client Error: Too Many Requests for url: https://api.groq.com/openai/v1/chat/completions"
  ]
}
```

## Test 9: WF009
**Prompt:** Assign this urgent development task to the best employee based on their skills and current workload. If nobody has both the required skills and enough capacity, escalate instead of assigning someone unsuitable.
**Files Available:** data/tasks.csv, data/employee_data.csv
**Router Decision:** WF009 (Expected: WF009)
**Missing Inputs:** []
**Execution Status:** completed_with_errors

### Output
```json
{
  "status": "completed_with_errors",
  "errors": [
    "LLM skill extraction failed: 429 Client Error: Too Many Requests for url: https://api.groq.com/openai/v1/chat/completions"
  ]
}
```

## Test 10: WF010
**Prompt:** Analyze the workflow execution logs and tell me which workflows are performing poorly. Include failure rate, average execution time, frequent errors, slow steps, and recommendations.
**Files Available:** data/workflow_logs.csv
**Router Decision:** WF010 (Expected: WF010)
**Missing Inputs:** []
**Execution Status:** completed_with_errors

### Output
```json
{
  "status": "completed_with_errors",
  "overall_summary": {
    "total_executions": 77,
    "successful": 69,
    "failed": 8
  },
  "workflow_metrics": [
    {
      "workflow_id": "WF007",
      "total_executions": 5,
      "failure_rate": 20.0,
      "average_execution_time": 0.0,
      "flagged": true,
      "frequent_errors": [
        {
          "error": "Campaign dates missing from request",
          "count": 1
        }
      ]
    },
    {
      "workflow_id": "WF005",
      "total_executions": 10,
      "failure_rate": 20.0,
      "average_execution_time": 0.0,
      "flagged": true,
      "frequent_errors": [
        {
          "error": "Shipment service timed out",
          "count": 1
        },
        {
          "error": "Order database connection reset",
          "count": 1
        }
      ]
    },
    {
      "workflow_id": "WF010",
      "total_executions": 4,
      "failure_rate": 0.0,
      "average_execution_time": 0.0,
      "flagged": false,
      "frequent_errors": []
    },
    {
      "workflow_id": "WF009",
      "total_executions": 8,
      "failure_rate": 0.0,
      "average_execution_time": 0.0,
      "flagged": false,
      "frequent_errors": []
    },
    {
      "workflow_id": "WF001",
      "total_executions": 10,
      "failure_rate": 0.0,
      "average_execution_time": 0.0,
      "flagged": false,
      "frequent_errors": []
    },
    {
      "workflow_id": "WF003",
      "total_executions": 10,
      "failure_rate": 30.0,
      "average_execution_time": 0.0,
      "flagged": true,
      "frequent_errors": [
        {
          "error": "Parser exception on malformed row 14",
          "count": 1
        },
        {
          "error": "No SKU column found in uploaded file",
          "count": 1
        },
        {
          "error": "Corrupt XLSX archive: unable to open workbook",
          "count": 1
        }
      ]
    },
    {
      "workflow_id": "WF002",
      "total_executions": 10,
      "failure_rate": 10.0,
      "average_execution_time": 0.0,
      "flagged": false,
      "frequent_errors": [
        {
          "error": "Vendor file has non-UTF-8 encoding (cp1252)",
          "count": 1
        }
      ]
    },
    {
      "workflow_id": "WF008",
      "total_executions": 6,
      "failure_rate": 0.0,
      "average_execution_time": 0.0,
      "flagged": false,
      "frequent_errors": []
    },
    {
      "workflow_id": "WF006",
      "total_executions": 6,
      "failure_rate": 0.0,
      "average_execution_time": 0.0,
      "flagged": false,
      "frequent_errors": []
    },
    {
      "workflow_id": "WF004",
      "total_executions": 8,
      "failure_rate": 12.5,
      "average_execution_time": 0.0,
      "flagged": true,
      "frequent_errors": [
        {
          "error": "LLM request timed out after 60s",
          "count": 1
        }
      ]
    }
  ],
  "slow_steps": "step-level timing unavailable",
  "recommendations": [],
  "errors": [
    "LLM Recommendation Error: 429 Client Error: Too Many Requests for url: https://api.groq.com/openai/v1/chat/completions"
  ]
}
```


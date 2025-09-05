
* 1. create new index mapping
```
PUT demo-logs-otel-v1-00001
{
      "mappings": {
      "dynamic_templates": [
        {
          "long_resource_attributes": {
            "path_match": "resource.attributes.*",
            "match_mapping_type": "long",
            "mapping": {
              "type": "long"
            }
          }
        },
        {
          "double_resource_attributes": {
            "path_match": "resource.attributes.*",
            "match_mapping_type": "double",
            "mapping": {
              "type": "double"
            }
          }
        },
        {
          "string_resource_attributes": {
            "path_match": "resource.attributes.*",
            "match_mapping_type": "string",
            "mapping": {
              "ignore_above": 256,
              "type": "keyword"
            }
          }
        },
        {
          "long_scope_attributes": {
            "path_match": "instrumentationScope.attributes.*",
            "match_mapping_type": "long",
            "mapping": {
              "type": "long"
            }
          }
        },
        {
          "double_scope_attributes": {
            "path_match": "instrumentationScope.attributes.*",
            "match_mapping_type": "double",
            "mapping": {
              "type": "double"
            }
          }
        },
        {
          "string_scope_attributes": {
            "path_match": "instrumentationScope.attributes.*",
            "match_mapping_type": "string",
            "mapping": {
              "ignore_above": 256,
              "type": "keyword"
            }
          }
        },
        {
          "long_attributes": {
            "path_match": "attributes.*",
            "match_mapping_type": "long",
            "mapping": {
              "type": "long"
            }
          }
        },
        {
          "double_attributes": {
            "path_match": "attributes.*",
            "match_mapping_type": "double",
            "mapping": {
              "type": "double"
            }
          }
        },
        {
          "string_attributes": {
            "path_match": "attributes.*",
            "match_mapping_type": "string",
            "mapping": {
              "ignore_above": 256,
              "type": "keyword"
            }
          }
        }
      ],
      "date_detection": false,
      "properties": {
        "@timestamp": {
          "type": "date_nanos"
        },
        "attributes": {
          "properties": {
            "0": {
              "type": "keyword",
              "ignore_above": 256
            },
            "@OrderResult": {
              "type": "keyword",
              "ignore_above": 256
            },
            "ContentRoot": {
              "type": "keyword",
              "ignore_above": 256
            },
            "EnvName": {
              "type": "keyword",
              "ignore_above": 256
            },
            "State": {
              "type": "keyword",
              "ignore_above": 256
            },
            "address": {
              "type": "keyword",
              "ignore_above": 256
            },
            "amount": {
              "properties": {
                "currencyCode": {
                  "type": "keyword",
                  "ignore_above": 256
                },
                "nanos": {
                  "type": "long"
                },
                "units": {
                  "properties": {
                    "high": {
                      "type": "long"
                    },
                    "low": {
                      "type": "long"
                    },
                    "unsigned": {
                      "type": "boolean"
                    }
                  }
                }
              }
            },
            "app": {
              "properties": {
                "order": {
                  "properties": {
                    "amount": {
                      "type": "double"
                    },
                    "id": {
                      "type": "keyword",
                      "ignore_above": 256
                    },
                    "items": {
                      "properties": {
                        "count": {
                          "type": "long"
                        }
                      }
                    }
                  }
                },
                "product": {
                  "properties": {
                    "id": {
                      "type": "keyword",
                      "ignore_above": 256
                    },
                    "name": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "shipping": {
                  "properties": {
                    "amount": {
                      "type": "double"
                    },
                    "tracking": {
                      "properties": {
                        "id": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                }
              }
            },
            "cardType": {
              "type": "keyword",
              "ignore_above": 256
            },
            "code": {
              "properties": {
                "file": {
                  "properties": {
                    "path": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "function": {
                  "properties": {
                    "name": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "line": {
                  "properties": {
                    "number": {
                      "type": "long"
                    }
                  }
                }
              }
            },
            "context": {
              "properties": {
                "total": {
                  "type": "double"
                }
              }
            },
            "destination": {
              "properties": {
                "address": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "event": {
              "properties": {
                "name": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "exception": {
              "properties": {
                "message": {
                  "type": "keyword",
                  "ignore_above": 256
                },
                "stacktrace": {
                  "type": "keyword",
                  "ignore_above": 256
                },
                "type": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "http": {
              "type": "keyword",
              "ignore_above": 256
            },
            "https": {
              "type": "keyword",
              "ignore_above": 256
            },
            "lastFourDigits": {
              "type": "keyword",
              "ignore_above": 256
            },
            "loyalty_level": {
              "type": "keyword",
              "ignore_above": 256
            },
            "name": {
              "type": "keyword",
              "ignore_above": 256
            },
            "otelServiceName": {
              "type": "keyword",
              "ignore_above": 256
            },
            "otelSpanID": {
              "type": "keyword",
              "ignore_above": 256
            },
            "otelTraceID": {
              "type": "keyword",
              "ignore_above": 256
            },
            "otelTraceSampled": {
              "type": "boolean"
            },
            "productId": {
              "type": "keyword",
              "ignore_above": 256
            },
            "products": {
              "type": "long"
            },
            "quantity": {
              "type": "long"
            },
            "quote": {
              "properties": {
                "cents": {
                  "type": "long"
                },
                "dollars": {
                  "type": "long"
                }
              }
            },
            "quote_service_addr": {
              "type": "keyword",
              "ignore_above": 256
            },
            "request": {
              "properties": {
                "amount": {
                  "properties": {
                    "currencyCode": {
                      "type": "keyword",
                      "ignore_above": 256
                    },
                    "nanos": {
                      "type": "long"
                    },
                    "units": {
                      "properties": {
                        "high": {
                          "type": "long"
                        },
                        "low": {
                          "type": "long"
                        },
                        "unsigned": {
                          "type": "boolean"
                        }
                      }
                    }
                  }
                },
                "creditCard": {
                  "properties": {
                    "creditCardCvv": {
                      "type": "long"
                    },
                    "creditCardExpirationMonth": {
                      "type": "long"
                    },
                    "creditCardExpirationYear": {
                      "type": "long"
                    },
                    "creditCardNumber": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                }
              }
            },
            "server": {
              "properties": {
                "address": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "source": {
              "properties": {
                "address": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "tracking_id": {
              "type": "keyword",
              "ignore_above": 256
            },
            "transactionId": {
              "type": "keyword",
              "ignore_above": 256
            },
            "transaction_id": {
              "type": "keyword",
              "ignore_above": 256
            },
            "upstream": {
              "properties": {
                "cluster": {
                  "type": "keyword",
                  "ignore_above": 256
                },
                "host": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "url": {
              "properties": {
                "full": {
                  "type": "keyword",
                  "ignore_above": 256
                },
                "path": {
                  "type": "keyword",
                  "ignore_above": 256
                },
                "query": {
                  "type": "keyword",
                  "ignore_above": 256
                },
                "template": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "urls": {
              "type": "keyword",
              "ignore_above": 256
            },
            "userId": {
              "type": "keyword",
              "ignore_above": 256
            },
            "user_agent": {
              "properties": {
                "original": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "user_currency": {
              "type": "keyword",
              "ignore_above": 256
            },
            "user_id": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "body": {
          "type": "text"
        },
        "droppedAttributesCount": {
          "type": "integer"
        },
        "flags": {
          "type": "long"
        },
        "instrumentationScope": {
          "properties": {
            "droppedAttributesCount": {
              "type": "integer"
            },
            "name": {
              "type": "keyword",
              "ignore_above": 128
            },
            "schemaUrl": {
              "type": "keyword",
              "ignore_above": 256
            },
            "version": {
              "type": "keyword",
              "ignore_above": 64
            }
          }
        },
        "observedTime": {
          "type": "object"
        },
        "observedTimestamp": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "resource": {
          "properties": {
            "attributes": {
              "properties": {
                "cluster_name": {
                  "type": "keyword",
                  "ignore_above": 256
                },
                "container": {
                  "properties": {
                    "id": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "host": {
                  "properties": {
                    "arch": {
                      "type": "keyword",
                      "ignore_above": 256
                    },
                    "name": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "log_name": {
                  "type": "keyword",
                  "ignore_above": 256
                },
                "node_name": {
                  "type": "keyword",
                  "ignore_above": 256
                },
                "os": {
                  "properties": {
                    "build_id": {
                      "type": "keyword",
                      "ignore_above": 256
                    },
                    "description": {
                      "type": "keyword",
                      "ignore_above": 256
                    },
                    "name": {
                      "type": "keyword",
                      "ignore_above": 256
                    },
                    "type": {
                      "type": "keyword",
                      "ignore_above": 256
                    },
                    "version": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "process": {
                  "properties": {
                    "command": {
                      "type": "keyword",
                      "ignore_above": 256
                    },
                    "command_args": {
                      "type": "keyword",
                      "ignore_above": 256
                    },
                    "command_line": {
                      "type": "keyword",
                      "ignore_above": 256
                    },
                    "executable": {
                      "properties": {
                        "name": {
                          "type": "keyword",
                          "ignore_above": 256
                        },
                        "path": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "owner": {
                      "type": "keyword",
                      "ignore_above": 256
                    },
                    "pid": {
                      "type": "long"
                    },
                    "runtime": {
                      "properties": {
                        "description": {
                          "type": "keyword",
                          "ignore_above": 256
                        },
                        "name": {
                          "type": "keyword",
                          "ignore_above": 256
                        },
                        "version": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "service": {
                  "properties": {
                    "instance": {
                      "properties": {
                        "id": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "name": {
                      "type": "keyword",
                      "ignore_above": 256
                    },
                    "namespace": {
                      "type": "keyword",
                      "ignore_above": 256
                    },
                    "version": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                },
                "telemetry": {
                  "properties": {
                    "distro": {
                      "properties": {
                        "name": {
                          "type": "keyword",
                          "ignore_above": 256
                        },
                        "version": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    },
                    "sdk": {
                      "properties": {
                        "language": {
                          "type": "keyword",
                          "ignore_above": 256
                        },
                        "name": {
                          "type": "keyword",
                          "ignore_above": 256
                        },
                        "version": {
                          "type": "keyword",
                          "ignore_above": 256
                        }
                      }
                    }
                  }
                },
                "zone_name": {
                  "type": "keyword",
                  "ignore_above": 256
                }
              }
            },
            "droppedAttributesCount": {
              "type": "integer"
            },
            "schemaUrl": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "schemaUrl": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "severity": {
          "properties": {
            "number": {
              "type": "integer"
            },
            "text": {
              "type": "keyword",
              "ignore_above": 32
            }
          }
        },
        "severityNumber": {
          "type": "long"
        },
        "severityText": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "spanId": {
          "type": "keyword",
          "ignore_above": 16
        },
        "time": {
          "type": "date_nanos"
        },
        "traceId": {
          "type": "keyword",
          "ignore_above": 32
        }
      }
    },
    "settings": {
      "index": {
        "number_of_shards": "1",
        "number_of_replicas": "1"
      }
    }
}
```
## 2. create pipeline
```
PUT _ingest/pipeline/copy-time-to-timestamp
{
  "processors": [
    {
      "set": {
        "if": "ctx.containsKey('time') && ctx.time != null",
        "field": "@timestamp",
        "value": "{{time}}"
      }
    }
  ]
}
```

## 3. _reindex
```
POST _reindex
{
  "source": {
    "index": "logs-otel-v1-000001"
  },
  "dest": {
    "index": "demo-logs-otel-v1-00001",
    "op_type": "create",
    "pipeline": "copy-time-to-timestamp"
  }
}
```
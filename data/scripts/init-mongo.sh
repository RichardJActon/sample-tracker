#!/usr/bin/env bash
 
echo "logging in as root user to create pims user and DB"

mongosh \
  --host localhost --port 27017 \
  -u "$MONGO_ROOT_USER" -p "$MONGO_ROOT_PWD" \
  --authenticationDatabase admin \
  --eval "use admin" \
  --eval "db.createUser({
      user: \"$APP_MONGO__USER\",
      pwd: \"$APP_MONGO__PWD\",
      roles: [
        {role: 'dbAdmin', db: \"$APP_MONGO__DATABASE\"},
        {role: 'readWrite', db: \"$APP_MONGO__DATABASE\"}
      ]
    })"

echo "Create test users"

mongosh \
  --host localhost --port 27017 \
  -u "$APP_MONGO__USER" -p "$APP_MONGO__PWD" \
  --authenticationDatabase admin \
  --eval "use $APP_MONGO__DATABASE" \
  --eval "db.createCollection('person')" \
  --eval "db.person.insertOne({
    'username': 'test',
    'given_name': 'test',
    'family_name': 'testington',
    'email': 'test@test.com',
    'email_verified': false,
    'disabled': false
  })" \
  --eval "db.person.insertOne({
    'username': 'admin',
    'given_name': 'admin',
    'family_name': 'admin',
    'email': 'admin@test.com',
    'email_verified': false,
    'disabled': false
  })"

    # 'failed_logins': [],
    # 'is_admin': true,

# NB add validator to people collection:
# https://www.mongodb.com/docs/manual/core/schema-validation/specify-json-schema/#std-label-schema-validation-json
# better examples than in the docs:
# https://jsonic.io/guides/json-schema-mongodb

# --eval "db.createCollection('people_collection', {
#     validator: {
#       \$jsonSchema: {
#         bsonType: 'object',
#         title: 'Person',
#         required: ['name', 'username', 'is_admin', 'email', 'disabled'],
#         properties: {
#           id: {
#             bsonType: 'string',
#             description: ''
#           },
#           name: {
#             bsonType: 'string',
#             description: ''
#           },
#           username: {
#             bsonType: 'string',
#           },
#           is_admin: {
#             bsonType: 'bool'
            
#           },
#           email: {
#             bsonType: 'string',
            
#           },
#           disabled: {
#             bsonType: 'bool'
            
#           }
#         },
#         additionalProperties: true
#       }
#     },
#     validationLevel: 'strict',
#     validationAction: 'error'
#   }
# )" \

import json

REQUIRED_PARAMS = ['city', 'bus_count', 'total_distance']

print('Loading function')


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept',
        },
    }


def handle_payload(payload):
    for param in REQUIRED_PARAMS:
        if param not in payload:
            return respond(None, "Please include a `" + param + "` argument")

    return respond(None, "All required parameters present!")


def lambda_handler(event, context):

    operations = {
        'DELETE': lambda dynamo, x: dynamo.delete_item(**x),
        'GET': lambda dynamo, x: dynamo.scan(**x),
        'POST': lambda dynamo, x: dynamo.put_item(**x),
        'PUT': lambda dynamo, x: dynamo.update_item(**x),
    }

    operation = event['httpMethod']
    if operation in operations:
        payload = event['queryStringParameters'] if operation == 'GET' else json.loads(event['body'])
        if (payload):
            return handle_payload(payload)
            # return respond(None, payload['friends'] if ('friends' in payload) else "Fish are friends, not food")
        else:
            return respond(None, "Please include arguments for `city`, `bus_count`, and `total_distance")
        # return respond(None, operations[operation](dynamo, payload))
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))

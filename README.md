# 🚂 🍣 Serverless Sushi Train

Serverless Sushi Train is a sample application (based on a fictitious restaurant of the same name), built using AWS Serverless technologies like SAM, EventBridge, API Gateway, Lambda, DynamoDB, SQS and Step Functions. The app comprises several loosely-coupled microservices which use a common event bus to choreograph their interactions.

## Scenario  

Customers at the restaurant use a tablet device to order dishes. When an order is placed, kitchen staff are notified and start preparing the dish. Once the dish is ready to be served it's swiftly delivered to the customer via a robotic sushi train. When the customer chooses to end their meal the tablet displays the total cost and prints out a slip they can present to the cashier. Restaurant policy dictates that any dish that takes longer than 30 seconds to serve is _free_ of charge.

<img src="./img/ui.png" alt="alt text" width="500px" border="1px">

## Architecture

<img src="./img/arch.png" alt="alt text" width="1100px" border="1px">

The solution is composed of:

- **Common event bus**: A serverless event bus that routes data between services using pattern-based rules.

- **Orders service**: A RESTful API allows customers to start a meal, order an item, and end a meal. Requests are handled by Lambda functions that persist data to a DynamoDB table. Data changes trigger a lambda function which in-turn publishes corresponding events to the event bus (```meal_started```, ```item_ordered```, ```meal_finished```). The service subscribes to ```item_served``` events which are pushed onto a queue and processed by a lambda function which updates the order records accordingly. 

- **Kitchen service**: This service receives ```item_ordered``` events in a queue and processes each order via a step function workflow. The workflow simulates the process of 'preparing' a dish by calculating a random preparation time (10 - 40 seconds), waiting for the dish to be ready, and then 'serving' the item on the sushi train - which raises an ```item_served``` event.

- **Billing service**: This service receives ```meal_finished``` events (which include details of items ordered and served) on a queue. A lambda function calculates the pricing of each dish, applies discounts, totals the bill, and records the result in table. A trigger function publishes a ```meal_billed``` event which includes the above billing information.

- **Notification service**: The client connects to a WebSocket API when the meal starts. The mapping between a meal and webSocket connection is recorded in a DynamoDB table. Events that the customer needs to be notified of (```item_served```, ```meal_billed```) invoke a lambda function that looks up the webSocket connection details and publishes a message back to the client.

- **Archiving/Monitoring**: A 'catch all' rule pushes all events to Kinesis Data Firehose which batches and writes raw JSON objects to an S3 bucket for long-term archival and analytics. A similar rule pushes all events to a Log Group in CloudWatch Logs (7 day retention) for diagnostic purposes. 

- **Static website assets**: HTML, JS, CSS resources. 

> **N.b. For the purposes of this sample application, both API gateway endpoints allow open (unauthenticated) access.**

## Deployment Steps 

### 1. Deploy SAM template

(Ensure you have the [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) installed before proceeding)

```bash
sam build
sam deploy --guided
```

### 2. Make note of the CloudFormation stack output values

- ```StaticWebBucket```
- ```WebSocketURL```
- ```WebsiteURL```
- ```EventLogGroup```
- ```RestApiURL```

### 3. Set API endpoints

```bash
cd client
```

Open ```index.js``` and set the constants at the top of the file to match the the stack output values ```RestApiURL``` and ```WebSocketURL``` :  

```
const restApiUrl = '';   // Set to RestApiURL
const webSocketUrl = '';    // Set to WebSocketURL
```

Save ```index.js``` 

### 5. Upload static content

While still in the ```client``` folder run the following command, replacing {StaticWebBucket} with the ```StaticWebBucket``` stack output value.

```bash
aws s3 cp . s3://{StaticWebBucket} --acl public-read --recursive
```

### 4. Open the website

Open the URL in the ```WebsiteURL``` stack output value. You can use the web UI to start a meal, order several items, wait for the items to arrive, and finish the meal. Refresh the page to start a new meal. 

## Understand

To see the events being published to the event bus, open CloudWatch Logs in the AWS console and open the Log Group indicated by the ```EventLogGroup``` stack output. 

<img src="./img/logs.png" alt="alt text" width="800px" border="1px">

When using the website you can can view API and WebSocket activity in the browser console.

## Cleanup

To delete the sample application use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
aws cloudformation delete-stack --stack-name serverless-sushi-train
```

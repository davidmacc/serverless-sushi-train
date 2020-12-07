////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

// Populate these settings using outputs from the CloudFormation stack
const restApiUrl = ''; // Example: 'https://avn1230he5.execute-api.ap-southeast-2.amazonaws.com/Prod'
const webSocketUrl = ''; // Examples: 'wss://71r45hj6l5.execute-api.ap-southeast-2.amazonaws.com/Prod'

////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////

let mealId;
let mealFinished = false;
let itemCount = 0;
let seatNum = Math.floor(Math.random() * 1000).toString();

const startMeal = async () => {
    const url = `${restApiUrl}/meals`;
    const response = await fetch(url, {
        method: 'POST',
        body: JSON.stringify({ seatNum: seatNum }),
    });
    const result = await response.json();
    this.mealId = result['mealId']
    console.log('meal ID: ' + this.mealId);
    document.querySelector('#mealNumDiv').innerHTML = `Meal ID: ${this.mealId}`;
    document.querySelector('#mealStartDiv').style.display = 'none';
    document.querySelector('#mealOrderDiv').style.display = 'block';

    wsUrl = `${webSocketUrl}?mealId=${this.mealId}`
    wsConn = new WebSocket(wsUrl);
    wsConn.onmessage = (event) => { processNotification(JSON.parse(event.data)); };
    wsConn.onopen = (event) => { console.log("WebSocket connection open."); };
    wsConn.onclose = (event) => { console.log("WebSocket connection closed."); };
    wsConn.onerror = (event) => { console.error("WebSocket error observed:", event); };
}

const orderItem = async (itemName) => {
    const apiUrl = `${restApiUrl}/meals/${this.mealId}/items`;
    const response = await fetch(apiUrl, {
        method: 'POST',
        body: JSON.stringify({ item: itemName, qty: 1 }),
    });
    const result = await response.json();
    const orderItemId = result['itemId'];
    const orderedTime = convertDate(result['orderedTime']).toTimeString().split(' ')[0]
    console.log('order item ID: ' + orderItemId);

    // Add ordered item to UI
    var itemRow = document.createElement("tr");
    itemRow.id = "item" + orderItemId;
    itemRow.innerHTML = `<td>${++itemCount}</td>`
        + `<td>${itemName}</td>`
        + `<td>${orderedTime}</td>`
        + '<td><div class="itemStatus">Preparing&nbsp;&nbsp;</div>'
        + '<div class="progress">'
        + '<div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar"'
        + 'aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%"></div></div>'
        + '<td></td>';
    document.querySelector("#orderedItemsTable tbody").appendChild(itemRow)
}

const endMeal = async () => {
    const apiUrl = `${restApiUrl}/meals/${this.mealId}`;
    const response = await fetch(apiUrl, {
        method: 'PATCH',
        body: '',
    });
    mealFinished = true;
    document.querySelector("#menuItemsDiv").style.display = 'none';
    document.querySelector("#endMealButton").style.display = 'none';
    document.querySelector("#billingProgress").style.display = 'flex';
    document.querySelectorAll("#orderedItemsTable .progress").forEach(function (x) { x.style.display = 'none'; });
}

function processNotification(e) {
    if (e.eventType == 'sushitrain.item_served') {
        if (!mealFinished) {
            console.log(e);
            delaySec = (convertDate(e.eventDetail.servedTime) - convertDate(e.eventDetail.orderedTime)) / 1000;
            statusTd = document.querySelectorAll('tr#item' + e.eventDetail.itemId + " > td")[3];
            statusTd.innerHTML = "✅ Served (" + delaySec.toFixed(0) + " sec)";
        }
    } else if (e.eventType == 'sushitrain.meal_billed') {
        console.log(e);
        document.querySelector("#billingProgress").style.display = 'none';
        document.querySelectorAll("#orderedItemsTable > thead > tr > th")[4].innerHTML = "Price";
        const mealItems = e.eventDetail.mealDetails.mealItems;
        let freeItems = 0;
        mealItems.forEach(function (orderItem) {
            priceTd = document.querySelectorAll('tr#item' + orderItem.itemId + " > td")[4];
            priceTd.innerHTML = orderItem.price == 0 ? "FREE" : "$" + orderItem.price.toFixed(2);
            if (orderItem.priceReasonCode == "SERVED_LATE") freeItems++;
        })
        document.querySelector("#paymentAlert").style.display = 'block';
        document.querySelector("#paymentAlert > h4").innerHTML = "Total cost: $" + e.eventDetail.totalPayment.toFixed(2);
        pSummary = document.querySelectorAll("#paymentAlert > p")[0];
        pSummary.innerHTML = `${freeItems} of ${mealItems.length} items are FREE of charge as they took longer than 30 seconds to arrive.`;
    }
}

function convertDate(date) {
    var arr = date.split(/[- :]/);
    return new Date(arr[0], arr[1]-1, arr[2], arr[3], arr[4], arr[5]);
}

document.querySelector("#seatDiv").innerHTML = `Seat No: ${seatNum}`;
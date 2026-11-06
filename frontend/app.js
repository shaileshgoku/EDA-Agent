const sessionId = crypto.randomUUID();


const questionInput =
    document.getElementById("question");

const askButton =
    document.getElementById("askButton");

const chatContainer =
    document.getElementById("chatContainer");

const showQueriesButton =
    document.getElementById("showQueriesButton");

const queriesContainer =
    document.getElementById("queriesContainer");

const newChatButton =
    document.getElementById("newChatButton");

const fileInput =
    document.getElementById("fileInput");

const uploadStatus =
    document.getElementById("uploadStatus");


let generatedQueries = [];



/*
==================================================
ASK AGENT
==================================================
*/

async function askAgent() {

    const question =
        questionInput.value.trim();


    if (!question) {
        return;
    }


    /*
    ----------------------------------------------
    ADD USER MESSAGE
    ----------------------------------------------
    */

    addMessage(
        "user",
        question
    );


    questionInput.value = "";


    /*
    ----------------------------------------------
    SHOW THINKING MESSAGE
    ----------------------------------------------
    */

    const thinkingMessage =
        addMessage(
            "agent",
            "Agent is analyzing your question..."
        );


    askButton.disabled = true;


    try {

        const response =
            await fetch(
                "http://127.0.0.1:8000/ask",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({

                        session_id:
                            sessionId,

                        question:
                            question

                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Agent request failed."
            );
        }


        /*
        ------------------------------------------
        REMOVE THINKING MESSAGE
        ------------------------------------------
        */

        thinkingMessage.remove();


        /*
        ------------------------------------------
        DISPLAY RESPONSE
        ------------------------------------------
        */

        displayAgentResponse(data);


    } catch (error) {

        thinkingMessage.textContent =
            `Error: ${error.message}`;

    } finally {

        askButton.disabled = false;

        questionInput.focus();

    }

}



/*
==================================================
SEND BUTTON
==================================================
*/

askButton.addEventListener(
    "click",
    askAgent
);



/*
==================================================
ENTER KEY
==================================================
*/

questionInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            askAgent();

        }

    }
);



/*
==================================================
ADD CHAT MESSAGE
==================================================
*/

function addMessage(
    role,
    content
) {

    const message =
        document.createElement("div");


    message.className =
        `message ${role}`;


    const bubble =
        document.createElement("div");


    bubble.className =
        "message-bubble";


    bubble.textContent =
        content;


    message.appendChild(
        bubble
    );


    chatContainer.appendChild(
        message
    );


    scrollToBottom();


    return bubble;

}



/*
==================================================
DISPLAY AGENT RESPONSE
==================================================
*/

function displayAgentResponse(data) {

    /*
    ----------------------------------------------
    TEXT RESPONSE
    ----------------------------------------------
    */

    const message =
        document.createElement("div");


    message.className =
        "message agent";


    const bubble =
        document.createElement("div");


    bubble.className =
        "message-bubble agent-response";


    bubble.textContent =
        data.text ||
        "No response received.";


    message.appendChild(
        bubble
    );


    chatContainer.appendChild(
        message
    );


    /*
    ----------------------------------------------
    CHARTS
    ----------------------------------------------
    */

    displayCharts(
        data.charts || []
    );


    /*
    ----------------------------------------------
    TABLES
    ----------------------------------------------
    */

    displayTables(
        data.tables || []
    );


    /*
    ----------------------------------------------
    GENERATED SQL
    ----------------------------------------------
    */

    generatedQueries =
        data.queries || [];


    if (
        generatedQueries.length > 0
    ) {

        showQueriesButton.style.display =
            "block";

    }


    scrollToBottom();

}



/*
==================================================
DISPLAY CHARTS
==================================================
*/

function displayCharts(charts) {

    charts.forEach(
        (chart, index) => {

            const chartCard =
                document.createElement("div");

            chartCard.className =
                "chart-card";


            const title =
                document.createElement("h3");

            title.textContent =
                `Chart ${index + 1}`;


            const chartDiv =
                document.createElement("div");


            chartCard.appendChild(
                title
            );

            chartCard.appendChild(
                chartDiv
            );


            chatContainer.appendChild(
                chartCard
            );


            Plotly.newPlot(
                chartDiv,
                chart.figure.data,
                chart.figure.layout,
                {
                    responsive: true
                }
            );

        }
    );

}



/*
==================================================
DISPLAY TABLES
==================================================
*/

function displayTables(tables) {

    tables.forEach(
        (table, index) => {

            const tableCard =
                document.createElement("div");

            tableCard.className =
                "table-card";


            const title =
                document.createElement("h3");

            title.textContent =
                `Result ${index + 1}`;


            const htmlTable =
                createHTMLTable(
                    table
                );


            tableCard.appendChild(
                title
            );

            tableCard.appendChild(
                htmlTable
            );


            chatContainer.appendChild(
                tableCard
            );

        }
    );

}



/*
==================================================
CREATE HTML TABLE
==================================================
*/

function createHTMLTable(table) {

    const htmlTable =
        document.createElement("table");


    const headerRow =
        document.createElement("tr");


    table.columns.forEach(
        column => {

            const th =
                document.createElement("th");


            th.textContent =
                column;


            headerRow.appendChild(
                th
            );

        }
    );


    htmlTable.appendChild(
        headerRow
    );


    table.rows.forEach(
        row => {

            const tableRow =
                document.createElement("tr");


            row.forEach(
                value => {

                    const td =
                        document.createElement("td");


                    td.textContent =
                        value === null
                            ? ""
                            : value;


                    tableRow.appendChild(
                        td
                    );

                }
            );


            htmlTable.appendChild(
                tableRow
            );

        }
    );


    return htmlTable;

}



/*
==================================================
SHOW / HIDE SQL
==================================================
*/

showQueriesButton.addEventListener(
    "click",
    () => {

        if (
            queriesContainer.innerHTML.trim()
        ) {

            queriesContainer.innerHTML =
                "";

            showQueriesButton.textContent =
                "Show SQL";

            return;

        }


        displayGeneratedQueries();


        showQueriesButton.textContent =
            "Hide SQL";

    }
);



/*
==================================================
DISPLAY GENERATED SQL
==================================================
*/

function displayGeneratedQueries() {

    queriesContainer.innerHTML =
        "";


    generatedQueries.forEach(
        (query, index) => {

            const queryCard =
                document.createElement("div");

            queryCard.className =
                "query-card";


            const title =
                document.createElement("h3");

            title.textContent =
                `SQL ${index + 1}`;


            const code =
                document.createElement("pre");


            const codeElement =
                document.createElement("code");


            codeElement.textContent =
                query.sql;


            code.appendChild(
                codeElement
            );


            queryCard.appendChild(
                title
            );

            queryCard.appendChild(
                code
            );


            queriesContainer.appendChild(
                queryCard
            );

        }
    );

}



/*
==================================================
NEW CHAT
==================================================
*/

newChatButton.addEventListener(
    "click",
    () => {

        chatContainer.innerHTML =
            `
            <div class="welcome-message">

                <h2>
                    How can I help you explore your data?
                </h2>

                <p>
                    Ask questions about distributions,
                    correlations, outliers, trends,
                    missing values, and more.
                </p>

            </div>
            `;

        queriesContainer.innerHTML =
            "";

        generatedQueries =
            [];

        showQueriesButton.textContent =
            "Show SQL";

        questionInput.focus();

    }
);



/*
==================================================
SCROLL TO BOTTOM
==================================================
*/

function scrollToBottom() {

    chatContainer.scrollTop =
        chatContainer.scrollHeight;

}
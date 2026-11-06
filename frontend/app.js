const sessionId = crypto.randomUUID();

const questionInput = document.getElementById("question");
const askButton = document.getElementById("askButton");
const chatContainer = document.getElementById("chatContainer");

const showQueriesButton =
    document.getElementById("showQueriesButton");

const showTablesButton =
    document.getElementById("showTablesButton");

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

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    addMessage("user", question);

    questionInput.value = "";

    const thinkingMessage = addMessage(
        "agent",
        "Agent is analyzing your question..."
    );

    askButton.disabled = true;

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/ask",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    session_id: sessionId,
                    question: question
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Agent request failed."
            );
        }

        thinkingMessage.remove();

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
    function (event) {

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

function addMessage(role, content) {

    const message = document.createElement("div");

    message.className = `message ${role}`;

    const bubble = document.createElement("div");

    bubble.className = "message-bubble";

    bubble.textContent = content;

    message.appendChild(bubble);

    chatContainer.appendChild(message);

    scrollToBottom();

    return bubble;
}



/*
==================================================
DISPLAY AGENT RESPONSE
==================================================
*/

function displayAgentResponse(data) {

    const message = document.createElement("div");

    message.className = "message agent";

    const bubble = document.createElement("div");

    bubble.className =
        "message-bubble agent-response";

    bubble.textContent =
        data.text || "No response received.";

    message.appendChild(bubble);

    chatContainer.appendChild(message);


    /*
    ----------------------------------------------
    DISPLAY CHARTS
    ----------------------------------------------
    */

    displayCharts(data.charts || []);


    /*
    ----------------------------------------------
    DISPLAY TABLES
    ----------------------------------------------
    */

    displayTables(data.tables || []);


    /*
    ----------------------------------------------
    STORE GENERATED SQL
    ----------------------------------------------
    */

    generatedQueries =
        data.queries || [];

    if (generatedQueries.length > 0) {

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

    charts.forEach(function (chart, index) {

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

        chartCard.appendChild(title);

        chartCard.appendChild(chartDiv);

        chatContainer.appendChild(chartCard);

        Plotly.newPlot(
            chartDiv,
            chart.figure.data,
            chart.figure.layout,
            {
                responsive: true
            }
        );

    });
}



/*
==================================================
DISPLAY QUERY RESULT TABLES
==================================================
*/

function displayTables(tables) {

    tables.forEach(function (table, index) {

        const tableCard =
            document.createElement("div");

        tableCard.className =
            "table-card";

        const title =
            document.createElement("h3");

        title.textContent =
            `Result ${index + 1}`;

        const htmlTable =
            createHTMLTable(table);

        tableCard.appendChild(title);

        tableCard.appendChild(htmlTable);

        chatContainer.appendChild(tableCard);

    });
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

    table.columns.forEach(function (column) {

        const th =
            document.createElement("th");

        th.textContent = column;

        headerRow.appendChild(th);

    });

    htmlTable.appendChild(headerRow);


    table.rows.forEach(function (row) {

        const tableRow =
            document.createElement("tr");

        row.forEach(function (value) {

            const td =
                document.createElement("td");

            td.textContent =
                value === null ? "" : value;

            tableRow.appendChild(td);

        });

        htmlTable.appendChild(tableRow);

    });

    return htmlTable;
}



/*
==================================================
SHOW / HIDE SQL
==================================================
*/

showQueriesButton.addEventListener(
    "click",
    function () {

        if (queriesContainer.innerHTML.trim()) {

            queriesContainer.innerHTML = "";

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

    queriesContainer.innerHTML = "";

    generatedQueries.forEach(
        function (query, index) {

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

            code.appendChild(codeElement);

            queryCard.appendChild(title);

            queryCard.appendChild(code);

            queriesContainer.appendChild(queryCard);

        }
    );
}



/*
==================================================
SHOW / HIDE DATA TABLES
==================================================
*/

showTablesButton.addEventListener(
    "click",
    async function () {

        const existingContainer =
            document.getElementById(
                "tablesContainer"
            );

        if (existingContainer) {

            existingContainer.remove();

            showTablesButton.textContent =
                "Show Tables";

            return;

        }

        try {

            showTablesButton.disabled = true;

            showTablesButton.textContent =
                "Loading...";

            const response =
                await fetch(
                    "http://127.0.0.1:8000/tables"
                );

            const data =
                await response.json();

            if (!response.ok) {

                throw new Error(
                    "Unable to load tables."
                );

            }

            displayTablesInSidebar(
                data.tables
            );

            showTablesButton.textContent =
                "Hide Tables";

        } catch (error) {

            showTablesButton.textContent =
                "Show Tables";

            alert(
                `Failed to load tables: ${error.message}`
            );

        } finally {

            showTablesButton.disabled = false;

        }

    }
);



/*
==================================================
DISPLAY DATA TABLES IN SIDEBAR
==================================================
*/

function displayTablesInSidebar(tables) {

    const container =
        document.createElement("div");

    container.id =
        "tablesContainer";

    container.className =
        "tables-sidebar";

    if (tables.length === 0) {

        container.textContent =
            "No datasets available.";

    }


    tables.forEach(function (tableName) {

        const tableItem =
            document.createElement("div");

        tableItem.className =
            "table-sidebar-item";

        tableItem.textContent =
            tableName;

        container.appendChild(tableItem);

    });


    queriesContainer.parentNode.insertBefore(
        container,
        queriesContainer
    );
}



/*
==================================================
NEW CHAT
==================================================
*/

newChatButton.addEventListener(
    "click",
    function () {

        chatContainer.innerHTML = `
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

        queriesContainer.innerHTML = "";

        const tablesContainer =
            document.getElementById(
                "tablesContainer"
            );

        if (tablesContainer) {
            tablesContainer.remove();
        }

        generatedQueries = [];

        showQueriesButton.textContent =
            "Show SQL";

        showTablesButton.textContent =
            "Show Tables";

        questionInput.focus();

    }
);



/*
==================================================
UPLOAD DATASET
==================================================
*/

fileInput.addEventListener(
    "change",
    async function () {

        const file =
            fileInput.files[0];

        if (!file) {
            return;
        }

        uploadStatus.textContent =
            "Uploading dataset...";

        try {

            const formData =
                new FormData();

            formData.append(
                "file",
                file
            );

            const response =
                await fetch(
                    "http://127.0.0.1:8000/upload",
                    {
                        method: "POST",
                        body: formData
                    }
                );

            const data =
                await response.json();

            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Dataset upload failed."
                );

            }

            uploadStatus.textContent =
                `Uploaded: ${data.table_name}`;

        } catch (error) {

            uploadStatus.textContent =
                `Upload failed: ${error.message}`;

        }

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
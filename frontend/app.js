const API_BASE_URL = "https://eda-agent-api.onrender.com";


// --------------------------------------------------
// Session
// --------------------------------------------------

let sessionId = crypto.randomUUID();


// --------------------------------------------------
// DOM Elements
// --------------------------------------------------

const questionInput = document.getElementById("question");
const askButton = document.getElementById("askButton");
const chatContainer = document.getElementById("chatContainer");

const fileInput = document.getElementById("fileInput");
const uploadStatus = document.getElementById("uploadStatus");

const showQueriesButton = document.getElementById(
    "showQueriesButton"
);

const showTablesButton = document.getElementById(
    "showTablesButton"
);

const queriesContainer = document.getElementById(
    "queriesContainer"
);

const newChatButton = document.getElementById(
    "newChatButton"
);


// --------------------------------------------------
// Ask Question
// --------------------------------------------------

async function askQuestion() {

    const question = questionInput.value.trim();

    if (!question) {
        return;
    }

    addMessage("user", question);

    questionInput.value = "";
    questionInput.style.height = "auto";

    showTypingIndicator();

    askButton.disabled = true;

    try {

        const response = await fetch(
            `${API_BASE_URL}/ask`,
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

        removeTypingIndicator();

        if (!response.ok) {

            addMessage(
                "agent",
                `Error: ${data.detail || "Agent request failed."}`
            );

            return;
        }

        renderAgentResponse(data);

    } catch (error) {

        removeTypingIndicator();

        addMessage(
            "agent",
            "Unable to connect to the EDA Agent backend."
        );

        console.error(error);

    } finally {

        askButton.disabled = false;

        questionInput.focus();
    }
}


// --------------------------------------------------
// Add Chat Message
// --------------------------------------------------

function addMessage(role, text) {

    const message = document.createElement("div");

    message.classList.add("message", role);

    const bubble = document.createElement("div");

    bubble.classList.add("message-bubble");

    bubble.textContent = text;

    message.appendChild(bubble);

    chatContainer.appendChild(message);

    scrollToBottom();
}


// --------------------------------------------------
// Typing Indicator
// --------------------------------------------------

function showTypingIndicator() {

    const message = document.createElement("div");

    message.id = "typingIndicator";

    message.classList.add(
        "message",
        "agent"
    );

    const bubble = document.createElement("div");

    bubble.classList.add(
        "message-bubble",
        "typing"
    );

    bubble.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;

    message.appendChild(bubble);

    chatContainer.appendChild(message);

    scrollToBottom();
}


function removeTypingIndicator() {

    const indicator = document.getElementById(
        "typingIndicator"
    );

    if (indicator) {
        indicator.remove();
    }
}


// --------------------------------------------------
// Render Agent Response
// --------------------------------------------------

function renderAgentResponse(data) {

    const message = document.createElement("div");

    message.classList.add(
        "message",
        "agent"
    );

    const bubble = document.createElement("div");

    bubble.classList.add(
        "message-bubble",
        "agent-response"
    );

    if (data.text) {

        const textElement = document.createElement("div");

        textElement.textContent = data.text;

        textElement.classList.add(
            "response-text"
        );

        bubble.appendChild(textElement);
    }

    message.appendChild(bubble);

    chatContainer.appendChild(message);


    // --------------------------------------------------
    // Render Tables
    // --------------------------------------------------

    if (
        data.tables &&
        data.tables.length > 0
    ) {

        data.tables.forEach(table => {

            renderTable(
                table,
                message
            );

        });
    }


    // --------------------------------------------------
    // Render Charts
    // --------------------------------------------------

    if (
        data.charts &&
        data.charts.length > 0
    ) {

        data.charts.forEach(chart => {

            renderChart(
                chart,
                message
            );

        });
    }


    // --------------------------------------------------
    // Store Generated SQL
    // --------------------------------------------------

    if (
        data.queries &&
        data.queries.length > 0
    ) {

        displayQueries(
            data.queries
        );
    }


    scrollToBottom();
}


// --------------------------------------------------
// Render Table
// --------------------------------------------------

function renderTable(table, parentElement) {

    if (
        !table.columns ||
        !table.rows
    ) {
        return;
    }

    const card = document.createElement("div");

    card.classList.add(
        "result-card"
    );

    const title = document.createElement("div");

    title.classList.add(
        "result-title"
    );

    title.textContent = "Query Result";

    card.appendChild(title);


    const tableWrapper = document.createElement("div");

    tableWrapper.classList.add(
        "table-wrapper"
    );

    const htmlTable = document.createElement("table");


    // Header

    const thead = document.createElement("thead");

    const headerRow = document.createElement("tr");

    table.columns.forEach(column => {

        const th = document.createElement("th");

        th.textContent = column;

        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);

    htmlTable.appendChild(thead);


    // Body

    const tbody = document.createElement("tbody");

    table.rows.forEach(row => {

        const tr = document.createElement("tr");

        row.forEach(value => {

            const td = document.createElement("td");

            td.textContent =
                value === null
                    ? "NULL"
                    : value;

            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });

    htmlTable.appendChild(tbody);

    tableWrapper.appendChild(
        htmlTable
    );

    card.appendChild(
        tableWrapper
    );

    parentElement.appendChild(card);
}


// --------------------------------------------------
// Render Chart
// --------------------------------------------------

function renderChart(chart, parentElement) {

    if (
        !chart.figure
    ) {
        return;
    }

    const card = document.createElement("div");

    card.classList.add(
        "result-card",
        "chart-card"
    );

    const chartContainer =
        document.createElement("div");

    chartContainer.classList.add(
        "chart-container"
    );

    card.appendChild(
        chartContainer
    );

    parentElement.appendChild(
        card
    );

    Plotly.newPlot(
        chartContainer,
        chart.figure.data,
        chart.figure.layout,
        {
            responsive: true,
            displayModeBar: true
        }
    );
}


// --------------------------------------------------
// Display Generated SQL
// --------------------------------------------------

function displayQueries(queries) {

    queriesContainer.innerHTML = "";

    queries.forEach((query, index) => {

        const queryCard =
            document.createElement("div");

        queryCard.classList.add(
            "query-card"
        );

        const title =
            document.createElement("div");

        title.classList.add(
            "query-title"
        );

        title.textContent =
            `Query ${index + 1}`;

        const sqlElement =
            document.createElement("pre");

        sqlElement.classList.add(
            "sql-code"
        );

        sqlElement.textContent =
            query.sql;

        queryCard.appendChild(
            title
        );

        queryCard.appendChild(
            sqlElement
        );

        queriesContainer.appendChild(
            queryCard
        );
    });
}


// --------------------------------------------------
// Show / Hide SQL
// --------------------------------------------------

showQueriesButton.addEventListener(
    "click",
    () => {

        const isVisible =
            queriesContainer.classList.contains(
                "visible"
            );

        if (isVisible) {

            queriesContainer.classList.remove(
                "visible"
            );

            showQueriesButton.textContent =
                "Show SQL";

        } else {

            queriesContainer.classList.add(
                "visible"
            );

            showQueriesButton.textContent =
                "Hide SQL";
        }
    }
);


// --------------------------------------------------
// Show Tables
// --------------------------------------------------

showTablesButton.addEventListener(
    "click",
    async () => {

        try {

            const response =
                await fetch(
                    `${API_BASE_URL}/tables`
                );

            const data =
                await response.json();

            renderTablesList(
                data.tables || []
            );

        } catch (error) {

            console.error(error);

            renderTablesList(
                []
            );
        }
    }
);


// --------------------------------------------------
// Render Tables List
// --------------------------------------------------

function renderTablesList(tables) {

    let existingContainer =
        document.getElementById(
            "tablesContainer"
        );

    if (existingContainer) {

        existingContainer.remove();
    }

    const container =
        document.createElement("div");

    container.id =
        "tablesContainer";

    container.classList.add(
        "tables-container"
    );


    if (tables.length === 0) {

        const message =
            document.createElement("p");

        message.textContent =
            "No tables available.";

        container.appendChild(
            message
        );

    } else {

        tables.forEach(table => {

            const tableItem =
                document.createElement("div");

            tableItem.classList.add(
                "table-item"
            );

            tableItem.textContent =
                table;

            container.appendChild(
                tableItem
            );
        });
    }

    showTablesButton.parentElement
        .appendChild(container);
}


// --------------------------------------------------
// File Upload
// --------------------------------------------------

fileInput.addEventListener(
    "change",
    async () => {

        const file =
            fileInput.files[0];

        if (!file) {
            return;
        }

        uploadStatus.textContent =
            "Uploading...";

        uploadStatus.classList.remove(
            "success",
            "error"
        );

        const formData =
            new FormData();

        formData.append(
            "file",
            file
        );

        try {

            const response =
                await fetch(
                    `${API_BASE_URL}/upload`,
                    {
                        method: "POST",
                        body: formData
                    }
                );

            const data =
                await response.json();

            if (!response.ok) {

                uploadStatus.textContent =
                    data.detail ||
                    "Upload failed.";

                uploadStatus.classList.add(
                    "error"
                );

                return;
            }

            uploadStatus.textContent =
                `Uploaded: ${data.table_name}`;

            uploadStatus.classList.add(
                "success"
            );

        } catch (error) {

            console.error(error);

            uploadStatus.textContent =
                "Unable to upload file.";

            uploadStatus.classList.add(
                "error"
            );
        }
    }
);


// --------------------------------------------------
// New Chat
// --------------------------------------------------

newChatButton.addEventListener(
    "click",
    () => {

        sessionId =
            crypto.randomUUID();

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

        queriesContainer.innerHTML =
            "";

        const tablesContainer =
            document.getElementById(
                "tablesContainer"
            );

        if (tablesContainer) {
            tablesContainer.remove();
        }

        uploadStatus.textContent =
            "";

        questionInput.value = "";

        questionInput.focus();

        scrollToBottom();
    }
);


// --------------------------------------------------
// Enter Key
// --------------------------------------------------

questionInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            askQuestion();
        }
    }
);


// --------------------------------------------------
// Auto Resize Textarea
// --------------------------------------------------

questionInput.addEventListener(
    "input",
    () => {

        questionInput.style.height =
            "auto";

        questionInput.style.height =
            `${questionInput.scrollHeight}px`;
    }
);


// --------------------------------------------------
// Send Button
// --------------------------------------------------

askButton.addEventListener(
    "click",
    askQuestion
);


// --------------------------------------------------
// Scroll to Bottom
// --------------------------------------------------

function scrollToBottom() {

    chatContainer.scrollTop =
        chatContainer.scrollHeight;
}
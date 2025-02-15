(() => {
  // Create and inject the sidebar UI into the webpage.
  function createSidebar() {
    if (document.getElementById("accessibility-sidebar")) return;

    const sidebar = document.createElement("div");
    sidebar.id = "accessibility-sidebar";
    sidebar.innerHTML = `
        <style>
          #accessibility-sidebar {
            position: fixed;
            top: 50px;
            right: 0;
            width: 300px;
            height: 100vh;
            background: #fff;
            box-shadow: -3px 0 10px rgba(0,0,0,0.2);
            z-index: 10000;
            padding: 15px;
            font-family: Arial;
            overflow-y: auto;
            border-left: 2px solid #007BFF;
          }
          #accessibility-input {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            box-sizing: border-box;
          }
          #accessibility-btn {
            width: 100%;
            padding: 10px;
            background: #007BFF;
            color: white;
            border: none;
            cursor: pointer;
          }
          #close-sidebar {
            position: absolute;
            top: 5px;
            right: 10px;
            cursor: pointer;
            font-size: 18px;
          }
        </style>
        <div id="close-sidebar">❌</div>
        <h3>Modify Accessibility</h3>
        <input id="accessibility-input" type="text" placeholder="e.g. Make text larger">
        <button id="accessibility-btn">Apply</button>
      `;
    document.body.appendChild(sidebar);

    // Close sidebar on clicking the "❌"
    document.getElementById("close-sidebar").addEventListener("click", () => {
      sidebar.remove();
    });

    // When the user clicks Apply, call scrapeAndModify with their request.
    document
      .getElementById("accessibility-btn")
      .addEventListener("click", () => {
        const userRequest = document
          .getElementById("accessibility-input")
          .value.trim();
        if (userRequest) {
          scrapeAndModify(userRequest);
        }
      });
  }

  // Function to send a POST request to the backend and retrieve AI-generated JS code.
  function scrapeAndModify(userRequest) {
    const pageHTML = document.documentElement.innerHTML;
    fetch("http://localhost:5000/modify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ request: userRequest, html: pageHTML }),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Generated JavaScript:", data.javascript);
        executeGeneratedScript(data.javascript);
      })
      .catch((error) => console.error("Error calling backend:", error));
  }

  // Function to inject and execute the AI-generated JavaScript code.
  function executeGeneratedScript(jsCode) {
    try {
      const script = document.createElement("script");
      script.textContent = jsCode;
      document.body.appendChild(script);
      console.log("Executed modifications.");
    } catch (error) {
      console.error("Error executing script:", error);
    }
  }

  // Run the sidebar injection immediately.
  createSidebar();
})();

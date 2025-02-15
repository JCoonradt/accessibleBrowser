chrome.action.onClicked.addListener(async (tab) => {
  // Inject content.js into the current page
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ["content.js"],
  });
});

(() => {
  const toastOptions = { delay: 6000 }

  function createToast(message) {

    // Clone the template
    const element = htmx.find("[data-toast-template]").cloneNode(true)

    // Remove the data-toast-template attribute
    delete element.dataset.toastTemplate

    // if (!tags.includes("dismissible")) {
      // remove header element
      // htmx.find(element, "[data-toast-dismissible]").remove()
      // element.className += "bg-info"
    // }

    // Set the CSS class
    element.className += " " + message.tags

    // Set the text
    htmx.find(element, "[data-toast-body]").innerText = message.message
    // htmx.find(element, "[data-toast-title]").innerText = message.message

    // Add the new element to the container
    htmx.find("[data-toast-container]").appendChild(element)

    // Show the toast using Bootstrap's API
    const toast = new bootstrap.Toast(element, toastOptions)
    toast.show()
  }

  htmx.on("messages", (event) => {
    event.detail.value.forEach(createToast)
  })

  // Show all existsing toasts, except the template
  htmx.findAll(".toast:not([data-toast-template])").forEach((element) => {
    const toast = new bootstrap.Toast(element, toastOptions)
    toast.show()
  })

})();
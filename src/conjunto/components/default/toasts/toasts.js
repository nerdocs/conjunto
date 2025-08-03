export default {
  delete_message(uid) {
    this.messages = this.messages.filter(msg => msg.uid !== uid);
  },
  add_message(message) {
    // save the message to the internal list, if not already saved (check uid!)
    if (!this.messages.some(m => m.uid === message.uid)) {
      this.messages.push(message)

      if(!message.dismissible) {
        // wait for the DOM to be settled before searching for #toast-{uid}
        this.$nextTick(() => {
          const toastElNodes = document.querySelectorAll(".toast:not(.dismissible)");
          toastElNodes.forEach((toastEl) => {
            const toast = new tabler.bootstrap.Toast(toastEl);
            toastEl.addEventListener('hidden.bs.toast', (event) => {
              this.delete_message(message.uid)
            })
            toast.show();
          })
        })
      }
    }
  }
}

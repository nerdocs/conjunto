from django.contrib.messages.storage.base import Message
from sourcetypes import javascript

from tetra import Component, public


class Toasts(Component):
    messages: list[Message] = public([])

    # language=javascript
    script: javascript = """
    export default {
        delete_message(uid) {
            this.messages = this.messages.filter(msg => msg.uid !== uid);
            console.log("deleted message", uid)
        },
        add_message(message) {
            // save the message to the internal list, if not already saved (uid!)
            if (!this.messages.some(m => m.uid === message.uid)) { 
                this.messages.push(message)
               
                if(!message.dismissible) {
                    // wait for the DOM to be settled before searching for #toast-{uid}
                    this.$nextTick(() => {
                        const toastElNodes = document.querySelectorAll(".toast:not(.dismissible)");
                        toastElNodes.forEach((toastEl) => {
                            const toast = new bootstrap.Toast(toastEl);
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
    """

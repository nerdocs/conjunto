(() => {
  const sortables = document.querySelectorAll('.sortable');
  sortables.forEach((sortable) => {
    new Sortable(sortable, {
      animation: 150,
      ghostClass: 'bg-info',
      handle: '.handle'
    })
  })

  // -------------- Modals --------------
  // Many thanks to Benoit Blanchon: https://blog.benoitblanchon.fr/django-htmx-modal-form/
  // let modal = new bootstrap.Modal(document.getElementById('modal'))  // hide the dialog at empty response.
  // This maybe additionally could check for status_core==204
  // document.addEventListener('htmx:beforeSwap', (e) => {
  //   // Empty response targeting #dialog => hide the modal
  //   if (e.detail.target.id === 'dialog' && !e.detail.xhr.response) {
  //     modal.hide()
  //     e.detail.shouldSwap = false
  //   }
  // })
  // document.addEventListener('htmx:afterSwap', (e) => {
  //   // Response targeting #dialog => show the modal
  //   if (e.detail.target.id === 'dialog') {
  //     modal.show()
  //   }
  // })

  // // set focus to first not-hidden input on modal (hidden = csrf_input, etc)
  // document.addEventListener('shown.bs.modal', (e) => {
  //   const modal = document.getElementById('modal')
  //   // not pretty, but works.
  //   // first try textareas
  //   const textareas = modal.querySelectorAll('textarea:not([type="hidden"])');
  //   for(const input of textareas) {
  //     if (!input.hidden) {
  //       input.focus()
  //       return
  //     }
  //   }
  //   // then input fields
  //   const inputs = modal.querySelectorAll('input:not([type="hidden"])');
  //   for(const input of inputs) {
  //     if (!input.hidden) {
  //       input.focus()
  //       return
  //     }
  //   }
  //   // if form contains no input fields, place focus on submit button
  //   submit = modal.querySelectorAll("button[type=submit]")
  //   if (submit && submit.length > 0) {
  //     submit[0].focus()
  //   } else {
  //     console.log("No input/textarea/submit button found to place focus.")
  //   }
  // })

  // empty the dialog on hide
  // document.addEventListener('hidden.bs.modal', () => {
  //   document.getElementById('dialog').innerHTML = ''
  // })

  // // Litepicker
  // const litepickers = document.querySelectorAll('.textinput');
  // console.log("registering ",litepickers)
  // litepickers.forEach((litepicker) => {
  //   new Litepicker({
  //     element: litepicker
  //   });
  // })

})();

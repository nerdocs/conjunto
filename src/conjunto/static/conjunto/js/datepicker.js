(() => {

  function convertDateFormat(djangoFormat) {
    // This is a hacky function to define the mapping
    // between Django and JavaScript date format strings
    const formatMap = {
      'Y': 'YYYY',
      'm': 'MM',
      'd': 'DD',
    };

    // Replace Django format chars with their JavaScript equivalents
    let jsFormat = '';
    for (let i = 0; i < djangoFormat.length; i++) {
      const char = djangoFormat.charAt(i);
      if (formatMap[char]) {
        jsFormat += formatMap[char];
      } else {
        jsFormat += char;
      }
    }
    return jsFormat;
  }


  const datePickerInputs = document.querySelectorAll('.datepickerinput');

  // create a map of {element.name => endElement} to keep track of end elements
  const elementsEndMap = {}
  for (const e of datePickerInputs) {
    let endFieldName = e.dataset.endField;
    if (endFieldName) {
      elementsEndMap[e.name] = document.getElementsByName(endFieldName)[0];
    }
  }
  datePickerInputs.forEach((e) => {
    if (e.dataset.endField) {
      const picker = new Litepicker({
        element: e,
        elementEnd: elementsEndMap[e.name],
        singleMode: false,
        allowRepick: true,
        lang: globals.LANGUAGE_CODE,
        format: convertDateFormat(get_format('SHORT_DATE_FORMAT')),
      })
      picker.on("selected", (date1, date2) => {
        elementsEndMap[e.name].focus()
      })
    } else {
      // only create a new litepicker if this element is not listed as end input!
      if(! Object.values(elementsEndMap).includes(e)) {
        const picker = new Litepicker({
          element: e,
          format: convertDateFormat(get_format('SHORT_DATE_FORMAT')),
          lang: globals.LANGUAGE_CODE,
        })
        picker.on("selected", (date1, date2) => {
          e.focus()
        })
      }

    }
  })


})();


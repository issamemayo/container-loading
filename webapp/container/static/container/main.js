function addForm() {
  var formIndex = document.querySelectorAll(".dynamic-form").length;
  var newForm = document.querySelector(".dynamic-form").cloneNode(true);
  newForm.innerHTML = newForm.innerHTML.replace(/__prefix__/g, formIndex);
  document.querySelector("#form-container").appendChild(newForm);
  document.querySelector("#id_form-TOTAL_FORMS").value = formIndex + 1;
}

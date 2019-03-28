import { initItemPage } from 'src/lib/itemPage.js'

import 'src/styles/aristotle_dse.css'

initItemPage()

// init toggle popovers
$('[data-toggle="popover"]').popover()


// This code is used by the collapsable Data Elements in the "Custers" section of the Dataset Specification page:
let coll = document.getElementsByClassName("collapsible");

for (let elem of coll) {
  elem.addEventListener("click", function() {
    this.classList.toggle("active");
    let content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
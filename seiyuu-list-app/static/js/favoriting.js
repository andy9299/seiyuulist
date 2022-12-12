"use strict";

const $editButton = $("#editButton");
const BASE_URL = "http://127.0.0.1:5000/favorite";



async function makeDraggable(evt) {
  console.debug("updateFavorite", evt);
  // grabbing the id from the url
  const seiyuu_id = $(location).attr('href').replace(/\/\s*$/, "").split('/').pop();
  await axios({
    url: `${BASE_URL}/seiyuu`,
    method: "POST",
    data: {
      seiyuu_id: seiyuu_id
    }
  });
  return;
}

$favorite.change("checkbox", updateFavorite);
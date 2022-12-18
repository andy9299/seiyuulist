"use strict";

const $favorite = $("#favorite");
const BASE_URL = window.location.protocol + "//" + window.location.host + "/";

async function updateFavorite(evt) {
  console.debug("updateFavorite", evt);
  // grabbing the id from the url
  const seiyuu_id = $(location).attr('href').replace(/\/\s*$/, "").split('/').pop();
  await axios({
    url: `${BASE_URL}favorite/seiyuu`,
    method: "POST",
    data: {
      seiyuu_id: seiyuu_id
    }
  });
  return;
}

$favorite.change("checkbox", updateFavorite);
"use strict";

const BASE_URL = window.location.protocol + "//" + window.location.host + "/";

console.log(BASE_URL);

function enableSorting(evt) {
  console.debug("enableSorting", evt);
  evt.preventDefault();
  $("#editButton").text('Save your ranking');
  $("#editButton").attr('id', 'saveButton');
  $("#seiyuuHolder").sortable();
  return;
}

async function saveRanking(evt) {
  console.debug("saveRanking", evt);
  evt.preventDefault();
  $("#seiyuuHolder").sortable("destroy");
  $("#saveButton").text('Edit seiyuu ranking');
  $("#saveButton").attr('id', 'editButton');
  var rankObj = {};
  $('.seiyuu').each(function (index) {
    rankObj[$(this).data('id')] = index + 1;
  }).toArray();
  console.log(rankObj);
  await axios({
    url: `${BASE_URL}rank/seiyuu`,
    method: "POST",
    data: rankObj
  });
  return;
}

$(document).on('click', "#editButton", enableSorting);
$(document).on('click', "#saveButton", saveRanking);



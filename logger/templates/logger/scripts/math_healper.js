function update_insulin() {
  var bg = document.getElementById('bloodsugar-helper').value;
  var carb = document.getElementById('carbs-helper').value;
  if(isNaN(bg)){
      bg = 0;
  };
  if(isNaN(carb)){
      carb = 0;
  };
  
  var insulin = Number(bg) + Number(carb);
  console.log(insulin);
  document.getElementById('insulin-helper').value = insulin;
}


function update_bg() {
  const bg = document.getElementById('id_bloodsugar').value;
  var insulin = ((bg - 200 )/ 50)* 0.5 + 1 ; // insulin calc here
  if(insulin < 0.5){
    document.getElementById('bloodsugar-helper').value = 0;
  }else{
  document.getElementById('bloodsugar-helper').value = insulin;
  }
  update_insulin();
}


function update_carbs() {
  const carbs = document.getElementById('id_carbs').value;
  const insul = Number(carbs) / 20;
  if(insul < 0.5){
    document.getElementById('carbs-helper').value = 0;
  }else{
  document.getElementById('carbs-helper').value = insul;
  }
  update_insulin();
}

$(document).ready(function(){
  $(':input', '#add_form')
    .trigger('reset');}
);

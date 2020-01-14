
// Intercept the submit, send the query to the server through Ajax, then load the results onto the page without reloading from the server
$(document).on('submit', '#search-form', function(ev){
  // Don't submit multiple times, don't automatically submit the form to the server
  ev.stopImmediatePropagation();
  ev.preventDefault();
  $('#loading-cover').show('fast');

  // Determine which button was clicked
  var active_button = $(document.activeElement).val();
  var url;
  if (active_button == "Search XML"){
    url = "/search/get-conditions/XML/";
  } else {
    url = "/search/get-conditions/";
  }
  var data = $(this).serialize();

  $.post(url, data, function(data){

    // Remove any previous data shown to make way for the new data to be displayed
    var symptomList = document.getElementById('symptom-list');
    if (symptomList){
      symptomList.remove();
    }

    var list = document.getElementById('condition-list');
    if (list){
      list.remove()
    }

    var symptomHeader = document.getElementById('symptom-header');
    if (symptomHeader){
      symptomHeader.remove();
    }

    var conditionHeader = document.getElementById('condition-header');
    if (conditionHeader){
      conditionHeader.remove();
    }

    var mainDiv = document.getElementById('form-div');

    // Check if we were able to find any symptoms in the query
    if (!data.symptoms_found){
      // Add a header explaining no results were found
      symptomHeader = document.createElement('h4');
      symptomHeader.innerHTML = "No symptoms matched your query";
      symptomHeader.id = 'symptom-header';
      mainDiv.appendChild(symptomHeader);
    } else {
      // We found at least one symptom. Populate lists for conditions and symptoms
      symptomList = document.createElement('ul');
      symptomList.id = 'symptom-list';

      list = document.createElement('ul');
      list.id = 'condition-list';

      for (var index = 0; index < data.symptoms.length; index++){
        var symptom = document.createElement('li');
        symptom.innerHTML = data.symptoms[index];
        symptomList.appendChild(symptom);
      }

      for (var index = 0; index < data.conditions.length; index++){
        var condition = document.createElement('li');
        condition.innerHTML = data.conditions[index];
        list.appendChild(condition);
      }

      symptomHeader = document.createElement('h4');
      symptomHeader.innerHTML = "Symptoms";
      symptomHeader.id = 'symptom-header';

      conditionHeader = document.createElement('h4');
      conditionHeader.innerHTML = "Related Conditions";
      conditionHeader.id = 'condition-header';

      // Append the headers and lists to the div holding the form
      mainDiv.appendChild(symptomHeader);
      mainDiv.appendChild(symptomList);
      mainDiv.appendChild(conditionHeader);
      mainDiv.appendChild(list)
    }
    $('#loading-cover').hide('slow');
  });
});

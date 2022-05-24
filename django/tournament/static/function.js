function highlightTeamClass(team) {
  $('td.team').removeClass('bg-warning')
  $('td.team-'+team).addClass('bg-warning')
}

function selectMatch(sid){
  if ($('#select' + sid).is(':checked')){
    $('.teamselector').prop('checked', false);
    $('#select' + sid).prop('checked', true);
    $('.teamswitch').each(function(){
      var oldUrl = $(this).attr('href');
      var newUrl = oldUrl.split('-').slice(0,3).join('-') + '-' + sid;
      $(this).attr('href', newUrl);
    })
  } else {
    $('.teamswitch').each(function(){
      var oldUrl = $(this).attr('href');
      var newUrl = oldUrl.split('-').slice(0,3).join('-') + '-xx';
      $(this).attr('href', newUrl);
    })
  }

  $("input:checkbox").prop('checked', $(this).prop("checked"));
}

//
// events
//
$(document).ready(function(){
  // changed score
  $("td.score input").change(
    function(){
      var input_el = this
      url = "/set/" +this.id + "/" + this.value;
      $.get(url)
      .done(
        function(){
          $(input_el).removeClass("bg-danger");
          $(input_el).addClass("bg-success");
          // focus na dalsi score pole - zatim funguje jen v radku
          $(input_el).closest('td.score').nextAll('td.score').first().find('input').focus();
        }
      )
      .fail(
        function(){
          $(input_el).addClass("bg-danger");
        }
      );
    }
  );

  // delete score
  $(".del-score").click(
    function(){
      var input_el = this
      url = "/del_score/match-" + this.name;
      $.get(url)
      .done(
        function(){
          $(input_el).removeClass("bg-danger");
          $(input_el).addClass("bg-success");
          location.reload();
        }
      )
      .fail(
        function(){
          $(input_el).addClass("bg-danger");
        }
      );
    }
  );

  $("#tgns").change(function(){
    $("tr.played").toggle(!this.checked);
  });

  $("button.finish-group").click(
    function(){
      var input_el = this
      url = "/finish/group-" +this.name;
      $.get(url)
      .done(
        function(){
          $(input_el).removeClass("bg-danger");
          $(input_el).addClass("bg-success");
        }
      )
      .fail(
        function(){
          $(input_el).addClass("bg-danger");
        }
      );
    }
  )
});

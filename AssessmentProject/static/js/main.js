window.addEventListener('resize', function(event) {
    const elem = this.document.getElementById('lastmitem')
    elem.style.height = (window.innerHeight - elem.offsetTop - 70) + "px"
}, true);


window.addEventListener('load', function(event) {
    const elem = this.document.getElementById('lastmitem')
    elem.style.height = (window.innerHeight - elem.offsetTop - 70) + "px"
    let e = document.getElementById("id_qtypesID");
    let qtypes = e.value;
    Array.prototype.forEach.call(document.getElementsByClassName('answer-change-i'), function(el) {
        el.type = "hidden"
        const newNode = document.createElement("input");
        newNode.checked = (el.value != '0')
        el.parentElement.insertBefore(newNode, el)
        newNode.name = 'answers-clickers'
        switch(qtypes){
            case '1':
                newNode.type = 'radio'
                newNode.className = 'answers-clickers'
                newNode.addEventListener('change', function(event1){
                    Array.prototype.forEach.call(document.getElementsByClassName('answer-change-i'), function(elem1){
                        console.log(elem1.name)
                        elem1.value = '0'
                    })
                    el.value = '1'
                }, true)
                break
            case '2':
                newNode.type = 'checkbox'
                newNode.className = 'answers-clickers'
                newNode.addEventListener('change', function(event){
                    el.value = event.target.checked ? 1 : 0
                    console.log(el.name, el.value, event.type)
                }, true)
                break
            default:
                newNode.type = 'hidden'
                newNode.className = 'answers-keyers'
        }
        
    })
    Array.prototype.forEach.call(document.getElementsByClassName('answer-change-r'), function(el) {
        if (qtypes!=3)
        {
            el.type = "hidden"
        }
    })
    /*
    document.getElementById('add-answer-button1').addEventListener('click', function(ev) {
        ev.preventDefault();
        var count = document.getElementById('item-answers').children.length
        var tmplMarkup = document.getElementById('answers-template').innerHTML
        var compiledTmpl = tmplMarkup.replace(/__prefix__/g, count)
        //document.getElementById('item-answers').append(compiledTmpl)
        document.getElementById('item-answers').innerHTML += compiledTmpl
    }, true);
    */
}, true);


$(document).ready(function() {
    // when user clicks add more btn of variants
      $('.add-answers').click(function(ev) {
          ev.preventDefault();
          var count = $('#item-answers').children().length;
          var tmplMarkup = $('#answers-template').html();
          var compiledTmpl = tmplMarkup.replace(/__prefix__/g, count);
          $('#item-answers').append(compiledTmpl);
  
          // update form count
          $('#id_variants-TOTAL_FORMS').attr('value', count+1);
      });
  });

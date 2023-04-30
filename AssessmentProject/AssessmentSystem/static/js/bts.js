var settings = {}

function getonum(onenum)
{
    if(onenum>9)return onenum
    return '0' + onenum
}

function show_q(id)
{
    Array.from(document.getElementsByClassName('testswitcher-item')).forEach((elem)=>{
        elem.classList.remove('testswitcher-item-sel')
    })
    document.getElementById('sw_' + id).classList.add('testswitcher-item-sel')
    data = settings['testdata']
    const quest = document.getElementById('quest-show')
    const answer = document.getElementById('answer-show')
    cur_id = settings['questorder'][id]
    quest.innerHTML = data['questions'][cur_id]['question']
    answer.innerHTML = ''

    if(data['questions'][cur_id]['type']==3)
    {
        let tmpE = document.createElement('div')
        tmpE.className = 'answer-item'
        tmpE.innerText = 'Введите Ваш вариант ответа:'
        answer.append(tmpE)
        let workelem = document.createElement('input')
        workelem.type = 'text'
        workelem.className = 'getanswers'
        workelem.name = 'quest_' + data['questions'][cur_id]['questionid']
        workelem.id = data['questions'][cur_id]['answers'][0]['answerid']
        workelem.style = 'margin-left: 20px;'
        tmpE.append(workelem)
        if(data['questions'][cur_id]['answers'][0]['answerid'] in settings['answers_for_upload']){
            workelem.value = settings['answers_for_upload'][data['questions'][cur_id]['answers'][0]['answerid']]['value']
        }else
        {
            settings['answers_for_upload'][data['questions'][cur_id]['answers'][0]['answerid']] = ({'assignmentid': data['assignment'],
                        'questid': data['questions'][cur_id]['questid'],
                        'type': data['questions'][cur_id]['type'],
                        'answer': data['questions'][cur_id]['answers'][0]['answerid'],
                        'value': ''
                    })
        }
        workelem.addEventListener('change', (elem)=>{
            settings['answers_for_upload'][data['questions'][cur_id]['answers'][0]['answerid']]['value'] = elem.target.value
            document.getElementById('sw_' + settings['questcurr']).classList.add('testswitcher-item-complete')
        })
    }else
    {
        let elemtype = 'radio'
        if(data['questions'][cur_id]['type']==2)elemtype = 'checkbox'
        data['questions'][cur_id]['answers'].forEach(
            element => 
            {
                let tmpE = document.createElement('div')
                tmpE.className = 'answer-item'
                answer.append(tmpE)

                let workelem = document.createElement('input')
                workelem.type = elemtype
                workelem.className = 'getanswers'
                workelem.name = 'quest_' + data['questions'][cur_id]['questionid']
                workelem.id = element['answerid']
                if(element['answerid'] in settings['answers_for_upload']){
                    workelem.value = settings['answers_for_upload'][element['answerid']]['value']
                    if(workelem.value==1)workelem.checked = true
                }else{
                    workelem.value = 0
                    settings['answers_for_upload'][element['answerid']] = ({'assignmentid': data['assignment'],
                        'questid': data['questions'][cur_id]['questid'],
                        'type': data['questions'][cur_id]['type'],
                        'answer': element['answerid'],
                        'value': 0
                    })
                }
                
                workelem.style = 'margin-right: 20px;'
                tmpE.append(workelem)
                if(data['questions'][cur_id]['type']==2)
                {
                    workelem.addEventListener('change', (elem)=>{
                        settings['answers_for_upload'][element['answerid']]['value'] = (elem.target.checked)?1:0
                        document.getElementById('sw_' + settings['questcurr']).classList.add('testswitcher-item-complete')
                    })
                }else
                {
                    workelem.addEventListener('change', (elem)=>{
                        Array.from(document.getElementsByClassName('getanswers')).forEach((elem)=>{
                            settings['answers_for_upload'][elem.id]['value'] = 0
                        })
                        settings['answers_for_upload'][element['answerid']]['value'] = (elem.target.checked)?1:0
                        document.getElementById('sw_' + settings['questcurr']).classList.add('testswitcher-item-complete')
                    })
                }
                

                let titlelem = document.createElement('span')
                titlelem.innerText = element['answer']
                tmpE.append(titlelem)
               console.log(settings['answers_for_upload'])
            }
        );
    }
    let tmpE = document.createElement('div')
    tmpE.className = 'answer-btn-item'
    answer.append(tmpE)
    let prevbtn = document.createElement('button')
    prevbtn.className = 'btn btn-primary'
    prevbtn.innerText = 'Предыдущий'
    prevbtn.style = 'margin-left:auto;margin-right:10px;'
    if(id==0)prevbtn.disabled = true
    tmpE.append(prevbtn)
    let nextbtn = document.createElement('button')
    nextbtn.className = 'btn btn-primary'
    nextbtn.innerText = "Следующий"
    nextbtn.style = 'margin-left:10px;margin-right:auto;'
    tmpE.append(nextbtn)
    if((id+1)==settings['questlen'])
    {
        nextbtn.innerText = "Завершить"
        nextbtn.addEventListener('click', fintest)
    }else
    {
        nextbtn.addEventListener('click', next)
    }
    prevbtn.addEventListener('click', prev)
}

function next()
{
    if(settings['questcurr']+1<settings['questlen'])settings['questcurr'] += 1
    show_q(settings['questcurr'])
}


function prev()
{
    if(settings['questcurr']>0)settings['questcurr'] -= 1
    show_q(settings['questcurr'])
}

function fintest()
{
    if( 'timer' in settings)clearInterval(settings['timer'])
    shadow.style = 'display:none;'

    $.ajax({
        type: 'POST',
        contentType : 'application/json',
        headers: {"X-CSRFTOKEN": window.CSRF_TOKEN},
        url: 'saveresults',
        data: JSON.stringify(settings['answers_for_upload']),
        success: function(data){
            location.reload()
        }
    })
}

function countdown()
{
    function newminute()
    {
        settings['minutes'] -= 1
        settings['seconds'] = 59
    }
    function newhour()
    {
        settings['hours'] -= 1
        settings['minutes'] = 59
        settings['seconds'] = 59
    }
    
    if (!('seconds' in settings) || !('minutes' in settings) || !('hours' in settings))
    {
        if( 'timer' in settings)clearInterval(settings['timer'])
        return
    }
    if(settings['seconds']>0)settings['seconds'] -= 1
    else if (settings['minutes']>0) newminute()
    else if (settings['hours']>0) newhour()

    if(settings['hours']<=0 && settings['minutes']<=0 && settings['seconds']<=0)fintest()

    document.getElementById('clock').innerHTML = getonum(settings['hours']) + " : " + getonum(settings['minutes']) + " : " + getonum(settings['seconds'])
}

function starttest(shadow)
{
    data = settings['testdata']
    $.ajax({type: 'GET', url: 'attemptstarted/' + data['assignment']})

    shadow.innerHTML = ''
    const blank = document.createElement('div')
    blank.className = 'blank-style'
    shadow.append(blank)

    const substrat = document.createElement('div')
    substrat.className = 'substrat-style'
    blank.append(substrat)

    const main = document.createElement('div')
    main.className = 'main-style'
    substrat.append(main)

    const menu = document.createElement('div')
    menu.className = 'menu-style'
    substrat.append(menu)

    const quest = document.createElement('div')
    quest.className = 'quest-style'
    quest.id = 'quest-show'
    main.append(quest)

    const answer = document.createElement('div')
    answer.className = 'answer-style'
    answer.id = 'answer-show'
    main.append(answer)

    const timer = document.createElement('div')
    timer.className = 'timer-style'
    timer.id = 'clock'
    menu.append(timer)
    
    const finish = document.createElement('div')
    finish.className = 'finish-style'
    menu.append(finish)

    const finishbtn = document.createElement('button')
    finishbtn.className = 'btn btn-primary'
    finishbtn.innerText = "Завершить"
    finishbtn.style = 'margin: 0 auto;'
    finish.append(finishbtn)
    finishbtn.addEventListener('click', fintest)
    
    const testswitcher = document.createElement('div')
    testswitcher.className = 'testswitcher-style'
    menu.append(testswitcher)

    settings['questlen'] = data['questions'].length
    settings['questorder'] = []
    settings['questcurr'] = 0
    settings['answers_for_upload'] = {}
    for (var i = 0; i < settings['questlen']; i++)
    {
        settings['questorder'].push(i);
    }
    if(data['randomseq'])
    {
        for (var i = 0; i < settings['questlen']; i++)
        {
            from = Math.floor(Math.random()*settings['questlen'])
            to = Math.floor(Math.random()*settings['questlen'])
            if(from!=to)
            {
                tmp = settings['questorder'][from]
                settings['questorder'][from] = settings['questorder'][to]
                settings['questorder'][to] = tmp
            }
        }
    }
    for (var i = 0; i < settings['questlen']; i++)
    {
        let tmpElem = document.createElement('div')
        tmpElem.className = 'testswitcher-item'
        tmpElem.id = 'sw_' + i
        tmpElem.value = i
        let tmpsubElem = document.createElement('div')
        tmpsubElem.className = 'testswitcher-item-number'
        tmpsubElem.id = 'iw_' + i
        tmpsubElem.value = i
        tmpsubElem.innerText = i+1
        testswitcher.append(tmpElem)
        tmpElem.append(tmpsubElem)
        tmpElem.addEventListener('click', (elem)=>{settings['questcurr']=elem.target.value;show_q(elem.target.value)})
    }
    if(data['duration']!=0) {
        settings['hours'] = Math.floor(data['duration'] / 60)
        settings['minutes'] = data['duration'] % 60
        settings['seconds'] = 0
        timer.innerText = getonum(settings['hours']) + " : " + getonum(settings['minutes']) + " : " + getonum(settings['seconds'])
        settings['timer'] = setInterval(countdown, 1000)
    }else
    {
        timer.innerText = "Без таймера"
    }
    show_q(settings['questcurr'])
}

function bts(testid, token)
{
    window.CSRF_TOKEN = token
    if(document.getElementById('shadow'))document.getElementById('shadow').remove();
    const shadow = document.createElement('div')
    shadow.className = 'shadow-style'
    shadow.id='shadow'
    document.body.append(shadow)

    const teststart = document.createElement('div')
    teststart.className = 'teststart-style'
    shadow.append(teststart)

    const testtitle = document.createElement('div')
    testtitle.className = 'testtitle-style'
    teststart.append(testtitle)

    const img = document.createElement('img')
    img.className = 'ajaxicon-style'
    img.src='../static/img/ajaxloadingicon.png'
    testtitle.append(img)

    const ttl = document.createElement('div')
    ttl.className = 'ttl-style'
    ttl.innerText = "Загрузка..."
    testtitle.append(ttl)

    $.ajax({
        type: 'GET',
        url: 'test/' + testid,
        success: function(data){
            if(data['quizid'])
            {
                settings['testdata'] = data
                testtitle.innerHTML = ""
                const testrulez = document.createElement('div')
                testrulez.className = 'testrulez-style'
                if(data['duration']==0)
                {
                    testrulez.innerHTML =   "Загружен тест: " + data['quizname'] + " \
                                        <br />Этот тест без таймера, Вы можете использовать любое количество времени на обдумывание ответов. <br /> \
                                        Тест начнётся и попытка будет засчитана после нажатия на кнопку 'Начать тест'."
                }else{
                    testrulez.innerHTML =   "Загружен тест: " + data['quizname'] + " \
                                        <br />На прохождение теста Вам даётся " + data['duration'] + " минут.<br /> \
                                        Таймер будет включен и попытка будет засчитана после нажатия на кнопку 'Начать тест'."                    
                }
                testtitle.append(testrulez)
                setTimeout(()=>{
                    const btns = document.createElement('div')
                    btns.className = 'startbtns-style'
                    testtitle.append(btns)
                    const cancelbutton = document.createElement('button')
                    cancelbutton.className = 'btn btn-primary startbtn-style'
                    cancelbutton.innerText = 'Отмена'
                    btns.append(cancelbutton)
                    cancelbutton.addEventListener('click', (elem)=>{shadow.style='display:none;'})

                    const startbutton = document.createElement('button')
                    startbutton.className = 'btn btn-primary startbtn-style'
                    startbutton.innerText = 'Начать тест'
                    btns.append(startbutton)
                    startbutton.addEventListener('click', (elem)=>{starttest(shadow)})
                }, 30)
            }else{
                shadow.style = 'display:none;'
            }
        }
    });

}
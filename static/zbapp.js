var sess = null;
var wsuri = "ws://" + window.location.hostname + ":8080/ws/api";
var retryCount = 0;
var retryDelay = 2;

var f1db = null;
var r1db = null;
var r2db = null;
var r3db = null;

var f1v = null;
var r1v = null;
var r2v = null;
var r3v = null;

var f1nd = null;
var r1nd = null;
var r2nd = null;
var r3nd = null;

var f1rx = null;
var r1rx = null;
var r2rx = null;
var r3rx = null;

var f1db_last = null;
var r1db_last = null;
var r2db_last = null;
var r3db_last = null;

var f1v_last = null;
var r1v_last = null;
var r2v_last = null;
var r3v_last = null;

var line0 = new TimeSeries();
var line1 = new TimeSeries();
var line2 = new TimeSeries();
var line3 = new TimeSeries();

var vline0 = new TimeSeries();
var vline1 = new TimeSeries();
var vline2 = new TimeSeries();
var vline3 = new TimeSeries();

var eventCnt = 0;
var eventCntUpdateInterval = 2;

function onND(topicUri, event) {
    eventCnt += 1;
    var stats = '';
    switch (event.value['device']) {
        case '00':
            stats = 'Coordinador';
            break;
        case '01':
            stats = 'Ruteador';
            break;
        case '02':
            stats = 'Final';
            break;
    }
    switch (event.id) {
        case 'F1':
            var oldrx = f1nd.innerHTML;
            f1nd.innerHTML = event.value['short'] + ':' + event.value['long'] + '-' + stats;
            break;
        case 'R1':
            var oldrx = r1nd.innerHTML;
            r1nd.innerHTML = event.value['short'] + ':' + event.value['long'] + '-' + stats;
            break;
        case 'R2':
            var oldrx = r2nd.innerHTML;
            r2nd.innerHTML = event.value['short'] + ':' + event.value['long'] + '-' + stats;
            break;
        case 'R3':
            var oldrx = r3nd.innerHTML;
            r3nd.innerHTML = event.value['short'] + ':' + event.value['long'] + '-' + stats;
            break;
        default:
            break;
    }
}

function onRX(topicUri, event) {
    eventCnt += 1;
    switch (event.id) {
        case 'F1':
            var oldrx = f1rx.innerHTML;
            f1rx.innerHTML = oldrx + event.value;
            break;
        case 'R1':
            var oldrx = r1rx.innerHTML;
            r1rx.innerHTML = oldrx + event.value;
            break;
        case 'R2':
            var oldrx = r2rx.innerHTML;
            r2rx.innerHTML = oldrx + event.value;
            break;
        case 'R3':
            var oldrx = r3rx.innerHTML;
            r3rx.innerHTML = oldrx + event.value;
            break;
        default:
            break;
    }
}
function onAnalogValue(topicUri, event) {
    eventCnt += 1;
    event.value = event.value; // / 400 * 100;
    event.value = event.value.toFixed(2);
    switch (event.id) {
        case 'F1':
            f1db.innerHTML = event.value;
            if (f1db_last !== null) {
                line0.append(new Date().getTime(), f1db_last);
            }
            f1db_last = event.value;
            line0.append(new Date().getTime(), event.value);
            break;
        case 'R1':
            r1db.innerHTML = event.value;
            if (r1db_last !== null) {
                line1.append(new Date().getTime(), r1db_last);
            }
            r1db_last = event.value;
            line1.append(new Date().getTime(), event.value);
            break;
        case 'R2':
            r2db.innerHTML = event.value;
            if (r2db_last !== null) {
                line2.append(new Date().getTime(), r2db_last);
            }
            r2db_last = event.value;
            line2.append(new Date().getTime(), event.value);
            break;
        case 'R3':
            r3db.innerHTML = event.value;
            if (r1db_last !== null) {
                line3.append(new Date().getTime(), r1db_last);
            }
            r3db_last = event.value;
            line3.append(new Date().getTime(), event.value);
            break;
        default:
            break;
    }
}

function onVolt(topicUri, event) {
    eventCnt += 1;
    event.value = event.value; // / 400 * 100;
    event.value = event.value.toFixed(2);
    switch (event.id) {
        case 'F1':
            f1v.innerHTML = event.value;
            if (f1v_last !== null) {
                vline0.append(new Date().getTime(), f1v_last);
            }
            f1v_last = event.value;
            vline0.append(new Date().getTime(), event.value);
            break;
        case 'R1':
            r1v.innerHTML = event.value;
            if (r1v_last !== null) {
                vline1.append(new Date().getTime(), r1v_last);
            }
            r1v_last = event.value;
            vline1.append(new Date().getTime(), event.value);
            break;
        case 'R2':
            r2v.innerHTML = event.value;
            if (r2v_last !== null) {
                vline2.append(new Date().getTime(), r2v_last);
            }
            r2v_last = event.value;
            vline2.append(new Date().getTime(), event.value);
            break;
        case 'R3':
            r3v.innerHTML = event.value;
            if (r1v_last !== null) {
                vline3.append(new Date().getTime(), r1v_last);
            }
            r3v_last = event.value;
            vline3.append(new Date().getTime(), event.value);
            break;
        default:
            break;
    }
}

function controlLed(status) {
    sess.call("rpc:control-led", status).always(ab.log);
}

function sendND(status) {
    sess.call("rpc:send-nd").always(ab.log);
}

function sendDBVOLT(status) {
    sess.call("rpc:send-dbvolt").always(ab.log);
}

function updateEventCnt() {
    document.getElementById("event-cnt").innerHTML = Math.round(eventCnt/eventCntUpdateInterval) + " events/s";
    eventCnt = 0;
}

function connect() {

    statusline = document.getElementById('statusline');

    sess = new ab.Session(wsuri,
            function() {

                statusline.innerHTML = "Connected to " + wsuri;
                retryCount = 0;

                sess.prefix("event", "http://example.com/mcu#");
                sess.subscribe("event:zb-db", onAnalogValue);
                sess.subscribe("event:zb-volt", onVolt);
                sess.subscribe("event:zb-nd", onND);
                sess.subscribe("event:zb-rx", onRX);
                //sess.subscribe("event:analog-value", onAnalogValue);

                sess.prefix("rpc", "http://example.com/mcu-control#");

                eventCnt = 0;

                window.setInterval(updateEventCnt, eventCntUpdateInterval * 1000);
            },
            function() {
                console.log(retryCount);
                retryCount = retryCount + 1;
                statusline.innerHTML = "Connection lost. Reconnecting (" + retryCount + ") in " + retryDelay + " secs ..";
                window.setTimeout(connect, retryDelay * 1000);
            }
    );
}


window.onload = function ()
{
    r1db = document.getElementById('xbeeR1db');
    r2db = document.getElementById('xbeeR2db');
    r3db = document.getElementById('xbeeR3db');
    f1db = document.getElementById('xbeeF1db');

    r1nd = document.getElementById('xbeeR1nd');
    r2nd = document.getElementById('xbeeR2nd');
    r3nd = document.getElementById('xbeeR3nd');
    f1nd = document.getElementById('xbeeF1nd');

    r1rx = document.getElementById('xbeeR1rx');
    r2rx = document.getElementById('xbeeR2rx');
    r3rx = document.getElementById('xbeeR3rx');
    f1rx = document.getElementById('xbeeF1rx');

    var smoothie = new SmoothieChart({grid: {strokeStyle: 'rgb(125, 0, 0)',
        fillStyle: 'rgb(171, 171, 255)',
        lineWidth: 1,
        //millisPerLine: 55000,
        verticalSections: 6},
        millisPerPixel:500,
        //interpolation: 'linear',
        minValue: 0,
        maxValue: 100,
        resetBounds: false,
        //interpolation: "line"
    });

    //smoothie.addTimeSeries(line0, { strokeStyle: 'rgb(0, 255, 0)', fillStyle: 'rgba(0, 255, 0, 0.4)', lineWidth: 3 });
    smoothie.addTimeSeries(line0, { strokeStyle: 'rgb(0, 115, 0)', lineWidth: 2 });
    smoothie.addTimeSeries(line1, { strokeStyle: 'rgb(255, 0, 255)', lineWidth: 2 });
    smoothie.addTimeSeries(line2, { strokeStyle: 'rgb(155, 50, 155)', lineWidth: 2 });
    smoothie.addTimeSeries(line3, { strokeStyle: 'rgb(55, 0, 55)', lineWidth: 2 });

    smoothie.streamTo(document.getElementById("dbs"));

    r1v = document.getElementById('xbeeR1volt');
    r2v = document.getElementById('xbeeR2volt');
    r3v = document.getElementById('xbeeR3volt');
    f1v = document.getElementById('xbeeF1volt');

    var vsmoothie = new SmoothieChart({grid: {strokeStyle: 'rgb(125, 0, 0)',
        fillStyle: 'rgb(171, 171, 255)',
        lineWidth: 1,
        verticalSections: 6},
        millisPerPixel: 500,
        minValue: 2.5,
        maxValue: 3.5,
        resetBounds: false,
        //interpolation: "line"
    });

    vsmoothie.addTimeSeries(vline0, { strokeStyle: 'rgb(0, 255, 0)', lineWidth: 3 });
    vsmoothie.addTimeSeries(vline1, { strokeStyle: 'rgb(255, 0, 255)', lineWidth: 3 });
    vsmoothie.addTimeSeries(vline2, { strokeStyle: 'rgb(155, 50, 155)', lineWidth: 3 });
    vsmoothie.addTimeSeries(vline3, { strokeStyle: 'rgb(55, 0, 55)', lineWidth: 3 });

    vsmoothie.streamTo(document.getElementById("volts"));
    connect();
};

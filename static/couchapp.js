var sess = null;
var wsuri = "ws://" + window.location.hostname + ":9001";
var retryCount = 0;
var retryDelay = 2;

var eventCnt = 0;
var eventCntUpdateInterval = 2;

function updateEventCnt() {
    document.getElementById("event-cnt").innerHTML = Math.round(eventCnt/eventCntUpdateInterval) + " events/s";
    eventCnt = 0;
}

function getGranjaInfo(granja) {
    sess.call("rpc:granja-info", granja).always(ab.log);
}
function getEstanqueInfo(granja) {
    sess.call("rpc:estanque-info", granja).always(ab.log);
}
function getSession(status) {
    sess.call("rpc:session-info", status).always(ab.log);
}
function doLogin(status) {
    sess.call("rpc:login", status).always(ab.log);
}
function doLogout(status) {
    sess.call("rpc:logout", status).always(ab.log);
}

function connect() {

    statusline = document.getElementById('statusline');

    sess = new ab.Session(wsuri,
            function() {

                statusline.innerHTML = "Connected to " + wsuri;
                retryCount = 0;

                sess.prefix("event", "http://www.tantan.org/db#");
                //sess.subscribe("event:analog-value", onAnalogValue);

                sess.prefix("rpc", "http://www.tantan.org/cmd-db#");

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

$(document).ready(function() {
    connect();
});

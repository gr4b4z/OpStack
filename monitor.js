var request = require('request');
var colors = require('colors');
var HTMLParser = require('fast-html-parser');

var loop = function () {
    opstackinfo();
    setTimeout(loop, 5000);
}
function formatName(n) {
    if (n.indexOf('node01') > -1 || n.indexOf('node02') > -1) {
        return n.magenta;
    } else if (n.indexOf('storage') > -1) {
        return n.cyan;
    } else if (n.indexOf('node') > -1) {
        return n.yellow;
    }
    return n.gray;
}
loop();
function opstackinfo() {


    request.get('http://10.122.252.16/nodes/status', {
        'auth': {
            'user': 'crowbar',
            'pass': 'crowbar',
            'sendImmediately': false
        },
        'headers': {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/javascript, */*; q=0.01'
        }
    }, function (error, response, body) {

        var servers = Object.keys(JSON.parse(body).nodes);
        var nodePromise = [];

        servers.forEach(element => {
            nodePromise.push(nodeinfo(element));
        });

        Promise.all(nodePromise).then(values => {
            process.stdout.write('\x1B[2J\x1B[0f');
            console.log("========================".blue + "========================".green);
            console.log("#                  Delta".blue + " OpenStack             #".green);
            console.log("========================".blue + "========================".green);

            values.forEach(f => {
                if (f.status) {

                    console.log(formatName(`Node: ${f.nodename}`));
                    f.networks.forEach(function (net_item) {
                        var term = `   ${net_item.name}${' '.repeat(7 - net_item.name.length)} : ${net_item.value}`;
                        if (term.indexOf('known') > -1) {
                            console.log(term.red);
                            return { nodename: f.nodename, status: false };
                        } else {
                            console.log(term);
                            return { nodename: f.nodename, status: true };
                        }
                    }, this);
                } else {
                    console.log(`Node: ${f.nodename}`.red)
                }
            });

        }).catch(e => {

            console.log(e);
        });


    });
}
function nodeinfo(nodename) {
    return new Promise(function (resolve, reject) {
        request.get('http://10.122.252.16/nodes/' + nodename, {
            'auth': {
                'user': 'crowbar',
                'pass': 'crowbar',
                'sendImmediately': false
            }
        }, function (error, response, body) {

            var root = HTMLParser.parse(body);
            // console.log(JSON.stringify(root.querySelector('table')));
            var d = root.querySelector('table');
            //        var headers = (d.childNodes[1].childNodes.filter(f=>!!f.childNodes).map(c=>c.childNodes.filter(f=>!!f.childNodes).map(t=>{return t.childNodes[0].rawText })).filter(b=>b.length == 4).map(t=>{return [{name:t[0],value:t[1]},{name:t[2],value:t[3]}] })).reduce(function(a, b) { return a.concat(b);});
            try {
                var networks = d.childNodes[1].childNodes.filter(f => !!f.childNodes)
                    .map(c => c.childNodes.filter(f => !!f.childNodes).map(t => { return { t: t.tagName, c: t.childNodes } }))
                    .filter(c => c.length == 2 && c[1].c.length == 3).map(r => r[1].c[1])[1].childNodes
                    .filter(t => t.childNodes)
                    .map(u => { return { f: u.childNodes[0].childNodes[0].rawText, y: u.childNodes[2].childNodes.map(t => t.childNodes[0].rawText) } })
                    .map(t => { return { name: t.f, value: t.y.join("|") } });

                resolve(
                    {
                        nodename: nodename,
                        networks: networks,
                        status: true
                    });
            } catch (error) {
                console.log("#######################################################################");
                console.log(JSON.stringify(d));
                resolve(
                    {
                        nodename: nodename,
                        status: false
                    });
            }

        });


    });


}


//  //nodes/status
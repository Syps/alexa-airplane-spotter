var express = require('express')
var app = express()
var PythonShell = require('python-shell')

var runPyScript = function(res) {
  PythonShell.run('live_speech_output.py', function (err, result) {
    if (err) throw err
    console.info(result)
    res.send(`{"response":"${result}"}`)
  })
}

app.get('/', function (req, res) {
  runPyScript(res)
})

app.listen(3000, function () {
  console.log('Example app listening on port 3000!')
})

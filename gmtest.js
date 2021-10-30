
// Test that imagemagick works https://stackoverflow.com/q/35874516/364931 
// node gmtest.js
var gm = require('gm').subClass({imageMagick: true});
const im = gm; //.subClass({imageMagick:true})

im(50, 50, '#000F')
    .setFormat('png') 
    .fill('black') 
    .antialias(false)
    .drawCircle( 50, 50, 60, 60 ) 
    .toBuffer(function( error, buffer ) {
        if( error ) { console.log( error ); return; }
        console.log( 'success: ' + buffer.length ); 
    } 
);

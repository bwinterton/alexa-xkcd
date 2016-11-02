var Alexa = require('alexa-sdk');
var parse = require('xml2js').parseString;
var request = require('request');


exports.handler = function(event, context, callback){
    var alexa = Alexa.handler(event, context);
	alexa.registerHandlers(handlers);
	alexa.execute();
};

var handlers = {

	// TODO: Handle the "Open XKCD" command correctly and store sessions

	// TODO "Is there a new XKCD?"
	'IsThereNewIntent' : function() {
	},

	// TODO: This needs to ask a question back to the user
	'AMAZON.HelpIntent' : function() {
		this.emit(':ask', "You can ask XKCD to get the latest post for you" +
				  " and I will send it to your phone!");
	},

	'AMAZON.StopIntent' : function() {
	},

	'AMAZON.CancelIntent' : function() {
	},

	'GetLatestIntent' : function() {
		var handler = this;
		request("http://xkcd.com/rss.xml", function (error, response, body) {
			if (!error && response.statusCode == 200) {
				parse(body, function (err, result) {
					//console.log(JSON.stringify(result, null, 4));
					var latest = result.rss.channel[0].item[0];
					var altre = new RegExp('alt="(.*)"');
					var numre = new RegExp('xkcd.com/([0-9]+)');
					var num = latest.link[0].match(numre)[1];
					var pic = "https://s3.amazonaws.com/xkcd-lambda/" + num + ".png";
					var latestPic= {
						smallImageUrl: pic,
						largeImageUrl: pic
					};
					var latestAlt = latest.description[0].match(altre)[1];
					latestAlt = latestAlt.replace(/&quot;/g,"\"")
					handler.emit(':tellWithCard',
								"The latest x-k-c-d is titled " + latest.title + ". I have sent it to your alexa app!",
								"Latest XKCD",
								 latest.title + "\n\n Alt: " + latestAlt,
								 latestPic);
				});
			} else {
				handler.emit(':tell', "I'm sorry, but I was unable to get the latest x-k-c-d");
			}
		});
	}
};

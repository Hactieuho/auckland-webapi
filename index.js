const express = require('express')
const app = express()
const bodyParser = require('body-parser')
const port = process.env.PORT || 80
var shell = require('shelljs');
const parse = require('csv-parse')
const fs = require('fs') 
const Collect = require('@supercharge/collections')

const ADDRESS_FILE='./Auckland_short.csv'
app.use(bodyParser.urlencoded({ extended: true }))
app.use(bodyParser.json())

var AddressList = []
ReadAddresData()

//Đọc tất cả dữ liệu csv =và đưa vào mảng
function ReadAddresData(){
    fs.createReadStream(ADDRESS_FILE)
        .pipe(parse({ delimiter: ',' }))
        .on('data', (r) => {
                                //console.log(r);
                                AddressList.push(r);        
                            })
        .on('end', () => {
                            console.log("Read csv completely");
                        })
}

app.use("/rubbish", function(req, res) {
    // crawl auckland data
    //let shellouput = shell.exec('scrapy runspider /crawler/myspider.py -a an="' + req.query.an +'"')
    let shellouput = shell.exec('/crawler/crawlwhat.sh "' + req.query.an +'"')
    
    // Get rid of "\n" from shelloutput.
    shellouput = shellouput.replace(/\r?'|\r/g, "\"")

    // Get rid of "\n" from shelloutput.
    shellouput = shellouput.replace(/\r?\n|\r/g, "")


    res.status(200).send(shellouput);
})

// Cấu trúc của AddressList
// suburb_locality	town_city	full_address_number	full_road_name
// Stanmore Bay	Whangaparaoa	14	Mably Court
// Stanmore Bay	Whangaparaoa	149	Brian Crescent
// URL  http://sinno.soict.ai:11080/town_citys
app.use("/town_citys", function(req, res) {
    col_town_city = AddressList.map(d => d[1]);
    res.status(200).send(    Collect(col_town_city).unique().all()  );
})

// Cấu trúc của AddressList
// suburb_locality	town_city	full_address_number	full_road_name
// Stanmore Bay	Whangaparaoa	14	Mably Court
// Stanmore Bay	Whangaparaoa	149	Brian Crescent
// URL  http://sinno.soict.ai:11080/suburb_localities?town_city=Auckland
app.use("/suburb_localities", function(req, res) {
    const town_city = (req.query.town_city == null)?'':req.query.town_city
    
    col_suburb_locality = AddressList.filter(c => c[1] == town_city).map(d => d[0]);
    res.status(200).send(    Collect(col_suburb_locality).unique().all()  );
})

// URL  http://sinno.soict.ai:11080/full_road_names?suburb_locality=Ruamahunga
app.use("/full_road_names", function(req, res) {
    const suburb_locality = (req.query.suburb_locality == null)?'':req.query.suburb_locality
    col_full_road_name = AddressList.filter(c => c[0] == suburb_locality).map(d => d[3]);
    res.status(200).send(    Collect(col_full_road_name).unique().all()  );
})


// URL  http://sinno.soict.ai:11080/full_address_numbers?suburb_locality=Ruamahunga&full_road_name=Pohue%20Creek%20Road
app.use("/full_address_numbers", function(req, res) {
    const suburb_locality = (req.query.suburb_locality == null)?'':req.query.suburb_locality
    const full_road_name = (req.query.full_road_name == null)?'':req.query.full_road_name

    col_full_address_number = AddressList.filter(c => c[0] == suburb_locality).filter(c => c[3] == full_road_name).map(d => d[2]);
    res.status(200).send(    Collect(col_full_address_number).unique().all()  );
})

app.use("/locations", function(req, res) {
    //const data = fs.readFileSync('./locations.json', {encoding:'utf8', flag:'r'});
    // suburb_locality=Ruamahunga
    // full_road_name=Pohue Creek Road
    // full_address_number=["13A","13"]
    //  --> 13A Pohue Creek Road, Ruamahunga
    //https://www.aucklandcouncil.govt.nz/property-rates-valuations/Pages/find-property-rates-valuation.aspx#deflectionLink
    //https://www.aucklandcouncil.govt.nz/_vti_bin/ACWeb/ACservices.svc/GetMatchingPropertyAddresses
    //Request Method: POST
    //Content-Type: application/json; charset=utf-8
    //_hjid=a210c99e-f275-4a1d-8d22-2170d4990117; _gid=GA1.3.1690226710.1624764859; WSS_FullScreenMode=false; _hjTLDTest=1; SearchSession=61521c61-5ae5-4fa2-9338-2213b5581bed; propertysearchpageflag=0; _ga_PFQWBEYHQF=GS1.1.1624903201.14.1.1624903864.0; _ga=GA1.3.529361729.1623914272; _gat_UA-16532671-41=1
    //{"ResultCount":"10","SearchText":"13A Pohue Creek Road, Ruamahung","RateKeyRequired":"false"}

    const suburb_locality = (req.query.suburb_locality == null)?'':req.query.suburb_locality
    const full_road_name = (req.query.full_road_name == null)?'':req.query.full_road_name    
    const full_address_number = (req.query.full_address_number == null)?'':req.query.full_address_number
    filter = full_address_number + " " + full_road_name + ", " + suburb_locality

    res.status(200).send(
        "Step 1 - Show and select town_citys: http://sinno.soict.ai:11080/town_citys <br/>" + 
        "Step 2 - Show and select suburb_locality (filted by town_citys) :  http://sinno.soict.ai:11080/suburb_localities?town_city=Auckland <br/>" +
        "Step 3 - Show and select full_road_name (filted by suburb_locality):  http://sinno.soict.ai:11080/full_road_names?suburb_locality=Ruamahunga <br/>" +
        "Step 4 - Show and select full_address_numbers (filted by suburb_locality and full_road_name):  http://sinno.soict.ai:11080/full_address_numbers?suburb_locality=Ruamahunga&full_road_name=Pohue%20Creek%20Road <br/>" +
        "Step 5 - Create full address=[full_address_numbers + full_road_name + ',' + suburb_locality]  and send it to get rubblish infor:  http://sinno.soict.ai:11080/rubbish?an=1 Pohue Avenue, Huapai<br/>"
    );
})



app.use(function(req, res) {
    res.status(404).send({url: req.originalUrl + ' not found. Try /rubbish?an='})
})

app.listen(port)

console.log('RESTful API server started on: ' + port)

## EMR Presto
* launch cli
```
presto-cli --catalog awsdatacatalog --schema default
```
* create table
```
CREATE TABLE prestohits (
  watchid BIGINT,
  javaenable SMALLINT,
  title VARCHAR,
  goodevent SMALLINT,
  eventtime BIGINT,
  eventdate DATE,
  counterid INTEGER,
  clientip INTEGER,
  regionid INTEGER,
  userid BIGINT,
  counterclass SMALLINT,
  os SMALLINT,
  useragent SMALLINT,
  url VARCHAR,
  referer VARCHAR,
  isrefresh SMALLINT,
  referercategoryid SMALLINT,
  refererregionid INTEGER,
  urlcategoryid SMALLINT,
  urlregionid INTEGER,
  resolutionwidth SMALLINT,
  resolutionheight SMALLINT,
  resolutiondepth SMALLINT,
  flashmajor SMALLINT,
  flashminor SMALLINT,
  flashminor2 VARCHAR,
  netmajor SMALLINT,
  netminor SMALLINT,
  useragentmajor SMALLINT,
  useragentminor VARCHAR,
  cookieenable SMALLINT,
  javascriptenable SMALLINT,
  ismobile SMALLINT,
  mobilephone SMALLINT,
  mobilephonemodel VARCHAR,
  params VARCHAR,
  ipnetworkid INTEGER,
  traficsourceid SMALLINT,
  searchengineid SMALLINT,
  searchphrase VARCHAR,
  advengineid SMALLINT,
  isartifical SMALLINT,
  windowclientwidth SMALLINT,
  windowclientheight SMALLINT,
  clienttimezone SMALLINT,
  clienteventtime TIMESTAMP,
  silverlightversion1 SMALLINT,
  silverlightversion2 SMALLINT,
  silverlightversion3 INTEGER,
  silverlightversion4 SMALLINT,
  pagecharset VARCHAR,
  codeversion INTEGER,
  islink SMALLINT,
  isdownload SMALLINT,
  isnotbounce SMALLINT,
  funiqid BIGINT,
  originalurl VARCHAR,
  hid INTEGER,
  isoldcounter SMALLINT,
  isevent SMALLINT,
  isparameter SMALLINT,
  dontcounthits SMALLINT,
  withhash SMALLINT,
  hitcolor VARCHAR,
  localeventtime TIMESTAMP,
  age SMALLINT,
  sex SMALLINT,
  income SMALLINT,
  interests SMALLINT,
  robotness SMALLINT,
  remoteip INTEGER,
  windowname INTEGER,
  openername INTEGER,
  historylength SMALLINT,
  browserlanguage VARCHAR,
  browsercountry VARCHAR,
  socialnetwork VARCHAR,
  socialaction VARCHAR,
  httperror SMALLINT,
  sendtiming INTEGER,
  dnstiming INTEGER,
  connecttiming INTEGER,
  responsestarttiming INTEGER,
  responseendtiming INTEGER,
  fetchtiming INTEGER,
  socialsourcenetworkid SMALLINT,
  socialsourcepage VARCHAR,
  paramprice BIGINT,
  paramorderid VARCHAR,
  paramcurrency VARCHAR,
  paramcurrencyid SMALLINT,
  openstatservicename VARCHAR,
  openstatcampaignid VARCHAR,
  openstatadid VARCHAR,
  openstatsourceid VARCHAR,
  utmsource VARCHAR,
  utmmedium VARCHAR,
  utmcampaign VARCHAR,
  utmcontent VARCHAR,
  utmterm VARCHAR,
  fromtag VARCHAR,
  hasgclid SMALLINT,
  refererhash BIGINT,
  urlhash BIGINT,
  clid INTEGER
)
WITH (
  format = 'PARQUET',
  external_location = 's3://flint-data-dp-us-west-2-beta/benchmark/clickbench/parquet/'
);
```
* query
```
SELECT 
  userid, 
  extract(minute FROM from_unixtime(eventtime)) AS m, 
  COUNT(*) 
FROM prestohits 
GROUP BY userid, extract(minute FROM from_unixtime(eventtime))
ORDER BY COUNT(*) DESC 
LIMIT 10
```

* debug UI
```
ssh -L 8889:localhost:8889 -i ~/tmp/pem/xxx.pem ec2-user@$presto
```
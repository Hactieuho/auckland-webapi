#!/bin/bash
#scrapy runspider myspider.py -a an=12342681539 2> null 

#Run on docker app1
scrapy runspider /root/crawler/myspider.py -a an="$1" 2> null 

#Run on the physical server
#scrapy runspider /home/app1/root/crawler/myspider.py -a an="$1" 2> null 
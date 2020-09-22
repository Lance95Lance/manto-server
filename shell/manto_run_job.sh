#!/bin/sh

parse_json() {
  value=$(echo $1 | sed 's/.*"success":\([^,}]*\).*/\1/')
  #    echo $value | sed 's/\"//g'

  if test ${value} == "false"; then
    echo "执行失败,退出"
    exit 1
  else
    echo "执行成功,退出"
    exit 0
  fi
}

url="http://127.0.0.1:4862/api/v1/scheduleDispatch"
#echo ${url}
curl ${url} -F batch_job_name=$1 >scheduleDispatch.json

# 提取response
res=$(cat scheduleDispatch.json) # eg: "district": "海淀区",
echo ${res}
echo "==================================="

parse_json ${res}

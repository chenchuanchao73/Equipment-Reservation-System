// 数据库表实时查看相关API
import axios from 'axios'

// 获取所有表名
export function getDbTables() {
  console.log("正在请求数据库表名...")
  return axios.get('/api/db/tables')
}

// 获取表字段结构
export function getDbTableColumns(tableName) {
  console.log("正在请求表字段结构:", tableName)
  return axios.get(`/api/db/table/${tableName}/columns`)
}

// 分页获取表数据
export function getDbTableRows(tableName, params) {
  console.log("正在请求表数据:", tableName, params)
  return axios.get(`/api/db/table/${tableName}/rows`, { params })
}
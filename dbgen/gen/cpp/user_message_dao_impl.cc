/* 
 *  Copyright (c) 2016, https://github.com/nebula-im/imengine 
 *  All rights reserved. 
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); 
 * you may not use this file except in compliance with the License. 
 * You may obtain a copy of the License at 
 * 
 *   http://www.apache.org/licenses/LICENSE-2.0 
 * 
 * Unless required by applicable law or agreed to in writing, software 
 * distributed under the License is distributed on an "AS IS" BASIS, 
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and 
 * limitations under the License. 
  */ 

#include "dal/usermessage_dao_impl.h"

UserMessageDAO& UserMessageDAO::GetInstance() {
  static UserMessageDAOImpl impl;
  return impl;
}

int64_t UserMessageDAOImpl::Create(UserMessageDO& user_message) {
  return DoStorageInsertID("nebula_engine",
  			[&](std::string& query_string) {
  			  db::QueryParam p;
  			  p.AddParam(user_message.passthrough_data.c_str());
  			  p.AddParam(user_message.user_id.c_str());
  			  p.AddParam(&user_message.message_content_type);
  			  p.AddParam(&user_message.client_message_id);
  			  p.AddParam(&user_message.peer_type);
  			  p.AddParam(user_message.message_content_data.c_str());
  			  p.AddParam(&user_message.updated_at);
  			  p.AddParam(user_message.sender_user_id.c_str());
  			  p.AddParam(&user_message.message_peer_seq);
  			  p.AddParam(&user_message.message_id);
  			  p.AddParam(&user_message.message_seq);
  			  p.AddParam(&user_message.created_at);
  			  p.AddParam(user_message.peer_id.c_str());
  			  p.AddParam(&user_message.id);

  			  db::MakeQueryString("INSERT INTO user_message"
  			  		"(status,passthrough_data,user_id,message_content_type,client_message_id,peer_type,message_content_data,updated_at,sender_user_id,message_peer_seq,message_id,message_seq,created_at,peer_id,id)"
  			  		" VALUES "
  			  		"(1,:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14)",
  			  		&p,
  			  		&query_string);
  			});
}

int UserMessageDAOImpl::LoadUserMessageList(const std::string& user_id, uint64_t received_max_message_seq, UserMessageDOList& user_message_list) {
  return DoStorageQuery("nebula_engine",
  			[&](std::string& query_string) {
  			  query_string = folly::sformat("SELECT status,passthrough_data,user_id,message_content_type,client_message_id,peer_type,message_content_data,updated_at,sender_user_id,message_peer_seq,message_id,message_seq,created_at,peer_id,id FROM user_message WHERE (user_id='{}' AND received_max_message_seq>{}) LIMIT 200",
  			  		user_id,received_max_message_seq
  			},
  			[&](db::QueryAnswer& answ) -> int {
  			  auto data = std::make_shared<UserMessageDO>();
  			  answ.GetColumn(0, &data.status);
  			  answ.GetColumn(1, &data.passthrough_data);
  			  answ.GetColumn(2, &data.user_id);
  			  answ.GetColumn(3, &data.message_content_type);
  			  answ.GetColumn(4, &data.client_message_id);
  			  answ.GetColumn(5, &data.peer_type);
  			  answ.GetColumn(6, &data.message_content_data);
  			  answ.GetColumn(7, &data.updated_at);
  			  answ.GetColumn(8, &data.sender_user_id);
  			  answ.GetColumn(9, &data.message_peer_seq);
  			  answ.GetColumn(10, &data.message_id);
  			  answ.GetColumn(11, &data.message_seq);
  			  answ.GetColumn(12, &data.created_at);
  			  answ.GetColumn(13, &data.peer_id);
  			  answ.GetColumn(14, &data.id);
  			  user_message_list.push_back(data);
  			  return CONTINUE;
  			});
}

int UserMessageDAOImpl::LoadUserDialogMessageList(const std::string& user_id, const std::string& peer_id, uint32_t peer_type, UserMessageDOList& user_message_list) {
  return DoStorageQuery("nebula_engine",
  			[&](std::string& query_string) {
  			  query_string = folly::sformat("SELECT status,passthrough_data,user_id,message_content_type,client_message_id,peer_type,message_content_data,updated_at,sender_user_id,message_peer_seq,message_id,message_seq,created_at,peer_id,id FROM user_message WHERE (user_id='{}' AND peer_id='{}' AND peer_type={}) LIMIT 200 OFFSET 0",
  			  		user_id,peer_id,peer_type
  			},
  			[&](db::QueryAnswer& answ) -> int {
  			  auto data = std::make_shared<UserMessageDO>();
  			  answ.GetColumn(0, &data.status);
  			  answ.GetColumn(1, &data.passthrough_data);
  			  answ.GetColumn(2, &data.user_id);
  			  answ.GetColumn(3, &data.message_content_type);
  			  answ.GetColumn(4, &data.client_message_id);
  			  answ.GetColumn(5, &data.peer_type);
  			  answ.GetColumn(6, &data.message_content_data);
  			  answ.GetColumn(7, &data.updated_at);
  			  answ.GetColumn(8, &data.sender_user_id);
  			  answ.GetColumn(9, &data.message_peer_seq);
  			  answ.GetColumn(10, &data.message_id);
  			  answ.GetColumn(11, &data.message_seq);
  			  answ.GetColumn(12, &data.created_at);
  			  answ.GetColumn(13, &data.peer_id);
  			  answ.GetColumn(14, &data.id);
  			  user_message_list.push_back(data);
  			  return CONTINUE;
  			});
}


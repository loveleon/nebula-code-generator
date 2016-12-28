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

#ifndef IMENGINE_DAL_USER_DO_H_ 
#define IMENGINE_DAL_USER_DO_H_ 

#include <list> 
#include <string> 

#include "dal/base_dal.h" 

struct UserDO { 
  uint64_t id{0};
  uint32_t app_id{1};
  std::string user_token;
  std::string user_id;
  std::string avatar;
  std::string nick;
  int is_active;
  int status;
  uint32_t created_at{0};
  uint32_t updated_at{0};

  META(id, app_id, user_token, user_id, avatar, nick, is_active, status, created_at, updated_at); 
};

using UserDOPtr = std::shared_ptr<UserDO>;
using UserDOList = std::list<UserDOPtr>;

#endif//IMENGINE_DAL_USER_DO_H_ 

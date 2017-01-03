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

#ifndef IMENGINE_DAL_USER_DAO_H_ 
#define IMENGINE_DAL_USER_DAO_H_ 

#include "dal/user_do.h"

struct UserDAO : public BaseDAO { 
  virtual ~UserDAO() = default; 

  static UserDAO& GetInstance(); 

  virtual int GetUserByUserID(uint32_t app_id, const std::string& user_id, UserDO& user_do) = 0;

  virtual int GetUserByToken(const std::string& app_key, const std::string& user_token, UserDO& user_do) = 0;

  virtual int GetUserByNamePasswd(uint32_t app_id, const std::string& user_id, const std::string& passwd, UserDO& user_do) = 0;

};

#endif//IMENGINE_DAL_USER_DAO_H_ 

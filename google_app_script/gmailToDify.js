// ============= 配置区 =============
const CONFIG = {
  // 你的 API 端点
  API_URL: 'https://<dify_host>/v1/workflows/run',
  
  // API Token（如果需要）
  API_TOKEN: '<API_TOKEN>',
  
  // 搜索条件（Gmail 搜索语法）
  SEARCH_QUERY: 'is:unread from:dan@tldrnewsletter.com',
  // 其他例子:
  // 'from:newsletter@substack.com is:unread'
  // 'subject:newsletter is:unread'
  // 'newer_than:1d is:unread'
  
  // 每次处理的邮件数量
  MAX_THREADS: 1,
  
  // 处理后的标签
  PROCESSED_LABEL: 'Processed/API',
  
  // 是否标记为已读
  MARK_AS_READ: true
};

// ============= 主函数 =============
function processNewEmails() {
  try {
    // 1. 确保标签存在
    ensureLabelExists(CONFIG.PROCESSED_LABEL);
    
    // 2. 搜索符合条件的邮件
    const threads = GmailApp.search(CONFIG.SEARCH_QUERY, 0, CONFIG.MAX_THREADS);
    
    Logger.log(`找到 ${threads.length} 个未处理的邮件线程`);
    
    // 3. 处理每个线程
    threads.forEach(thread => {
      const messages = thread.getMessages();
      
      messages.forEach(message => {
        if (message.isUnread()) {
          processMessage(message);
        }
      });
      
      // 4. 添加标签和标记已读
      const label = GmailApp.getUserLabelByName(CONFIG.PROCESSED_LABEL);
      thread.addLabel(label);
      
      if (CONFIG.MARK_AS_READ) {
        thread.markRead();
      }
    });
    
    Logger.log('处理完成');
    
  } catch (error) {
    Logger.log('错误: ' + error.toString());
    // 可选：发送错误通知邮件给自己
    sendErrorNotification(error);
  }
}

function parseTLDRArticles(text) {
  // 移除前缀（🚀 之前的内容）和后缀（Love TLDR 之后的内容）
  const startMarker = '🚀';
  const endMarker = 'Love TLDR? Tell your friends and get rewards!';
  
  let startIndex = text.indexOf(startMarker);
  let endIndex = text.indexOf(endMarker);
  
  if (startIndex === -1) startIndex = 0;
  if (endIndex === -1) endIndex = text.length;
  
  const mainContent = text.substring(startIndex, endIndex).trim();
  
  // 定义类别及其对应的emoji标识
  const categories = [
    { emoji: '🚀', name: 'HEADLINES & LAUNCHES' },
    { emoji: '🧠', name: 'DEEP DIVES & ANALYSIS' },
    { emoji: '🧑‍💻', name: 'ENGINEERING & RESEARCH' },
    { emoji: '🎁', name: 'MISCELLANEOUS' },
    { emoji: '⚡', name: 'QUICK LINKS' }
  ];
  
  // 分割内容到不同类别
  const sections = [];
  
  for (let i = 0; i < categories.length; i++) {
    const currentCategory = categories[i];
    const nextCategory = categories[i + 1];
    
    // 查找当前类别的起始位置（emoji + 类别名称）
    const categoryPattern = new RegExp(`${currentCategory.emoji}\\s*\\n\\s*${currentCategory.name}`, 'i');
    const categoryMatch = mainContent.match(categoryPattern);
    
    if (!categoryMatch) continue;
    
    const sectionStart = mainContent.indexOf(categoryMatch[0]) + categoryMatch[0].length;
    
    // 确定类别内容的结束位置
    let sectionEnd = mainContent.length;
    if (nextCategory) {
      const nextPattern = new RegExp(`${nextCategory.emoji}\\s*\\n\\s*${nextCategory.name}`, 'i');
      const nextMatch = mainContent.match(nextPattern);
      if (nextMatch) {
        sectionEnd = mainContent.indexOf(nextMatch[0]);
      }
    }
    
    const sectionContent = mainContent.substring(sectionStart, sectionEnd).trim();
    
    sections.push({
      category: currentCategory.name,
      emoji: currentCategory.emoji,
      content: sectionContent
    });
  }
  
  // 从每个类别中提取文章
  const allArticles = [];
  
  sections.forEach(section => {
    const articles = extractArticlesFromSection(section.content, section.category);
    allArticles.push(...articles);
  });
  
  return allArticles;
}

function extractArticlesFromSection(content, category) {
  const articles = [];
  
  // 匹配标题模式：文本 + (数字 MINUTE READ) [数字]
  const titlePattern = /^(.+?)\s+\((\d+\s+MINUTE\s+READ)\)\s+\[(\d+)\]/gm;
  
  const matches = [];
  let match;
  
  while ((match = titlePattern.exec(content)) !== null) {
    matches.push({
      fullMatch: match[0],
      title: match[1].trim(),
      readTime: match[2],
      link: match[3],
      index: match.index
    });
  }
  
  // 提取每篇文章的内容
  for (let i = 0; i < matches.length; i++) {
    const currentMatch = matches[i];
    const nextMatch = matches[i + 1];
    
    // 确定内容的起始和结束位置
    const contentStart = currentMatch.index + currentMatch.fullMatch.length;
    const contentEnd = nextMatch ? nextMatch.index : content.length;
    
    // 提取并清理内容
    let articleContent = content.substring(contentStart, contentEnd).trim();
    
    articles.push({
      category: category,
      title: currentMatch.title,
      content: articleContent
    });
  }
  
  return articles;
}

// ============= 处理单封邮件 =============
function processMessage(message) {
  try {
    // 提取邮件数据
    const emailData = {
      id: message.getId(),
      // threadId: message.getThread().getId(),
      from: message.getFrom(),
      // to: message.getTo(),
      // cc: message.getCc(),
      subject: message.getSubject(),
      // date: message.getDate().toISOString(),
      
      // 邮件内容
      articles: parseTLDRArticles(message.getPlainBody()),
      // htmlBody: message.getBody(),
      
      // 附件信息
      // attachments: message.getAttachments().map(att => ({
      //   name: att.getName(),
      //   size: att.getSize(),
      //   type: att.getContentType()
      // }))
    };
    
    Logger.log(`处理邮件: ${emailData.subject}`);
    emailData.articles.forEach((article, index) => {
      Logger.log(`\n========== 文章 ${index + 1} ==========`);
      Logger.log(`类别: ${article.category}`);
      Logger.log(`标题: ${article.title}`);
      Logger.log(`内容:\n${article.content}`);
      sendToAPI(article)
    });

    // 调用 API
    // sendToAPI(emailData);
    
  } catch (error) {
    Logger.log(`处理邮件失败: ${error.toString()}`);
    throw error;
  }
}

// ============= 发送到 API =============
function sendToAPI(article) {
  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: {
      'Authorization': 'Bearer ' + CONFIG.API_TOKEN,
      'Content-Type': 'application/json'
    },
    payload: JSON.stringify({
      inputs: article,
      response_mode: "blocking",
      user: "google_script"
    })
  };
  
  try {
    const response = UrlFetchApp.fetch(CONFIG.API_URL, options);
    const statusCode = response.getResponseCode();
    
    if (statusCode === 200 || statusCode === 201) {
      Logger.log(`✓ API 调用成功: ${article.title}`);
    } else {
      Logger.log(`✗ API 返回错误 ${statusCode}: ${response.getContentText()}`);
    }
    
  } catch (error) {
    Logger.log(`✗ API 调用失败: ${error.toString()}`);
    // 不抛出错误，继续处理其他邮件
  }
}

// ============= 辅助函数 =============
function ensureLabelExists(labelName) {
  let label = GmailApp.getUserLabelByName(labelName);
  if (!label) {
    // 支持嵌套标签 "Parent/Child"
    const parts = labelName.split('/');
    let currentLabel = null;
    let currentPath = '';
    
    parts.forEach(part => {
      currentPath = currentPath ? `${currentPath}/${part}` : part;
      currentLabel = GmailApp.getUserLabelByName(currentPath);
      if (!currentLabel) {
        currentLabel = GmailApp.createLabel(currentPath);
      }
    });
    
    label = currentLabel;
  }
  return label;
}

function sendErrorNotification(error) {
  const subject = '[Gmail Script] 处理邮件时出错';
  const body = `
错误时间: ${new Date().toLocaleString()}
错误信息: ${error.toString()}
堆栈跟踪: ${error.stack}

请检查脚本日志获取更多信息:
https://script.google.com
  `;
  
  MailApp.sendEmail(Session.getActiveUser().getEmail(), subject, body);
}

// ============= 手动测试函数 =============
function testAPI() {
  const testData = {
    id: 'test-123',
    subject: 'Test Email',
    from: 'ybalbert@xxxx.com',
    plainBody: "this is a test - 2"
  };
  
  sendToAPI(testData);
  Logger.log('测试完成，请检查日志');
}

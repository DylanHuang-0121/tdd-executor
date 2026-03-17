# Java TDD 示例：单元测试编写规范

## 📋 来源

Based on: `/Users/dylan/IdeaProjects/pcreditagreement/app/test/src/test/java/com/alipay/pcreditagreement/testng/test/unit/card/CardManagementServiceUnitTest.java`

---

## 🔧 文件位置

```
tdd-toolkit/examples/
└── java-tdd-example.md  # 本文件
└── tdd/
    └── java/             # Java TDD 示例目录（可选）
        └── CardManagementServiceUnitTest.java
```

---

## 🎯 测试结构设计

### **测试类结构**

```java
@TestClass
@DataProviderFactory
public class CardManagementServiceUnitTest {
    
    @Mock
    private CardManagementService service;
    
    @Mock
    private CardManager cardManager;
    
    @Mock
    private Logger logger;
    
    @BeforeClass
    public void setUp() {
        // 初始化 Mock 对象
        MockUtils.initMock(new Object[]{service, cardManager, logger});
        this.service = PowerMockito.mock(CardManagementService.class);
    }
    
    @AfterClass
    public void tearDown() {
        PowerMockito.resetAll();
    }
}
```

---

## 📝 测试用例模板

### **模板 1: 正常路径测试**

```java
@Test
public void testAddCard_Success() throws Exception {
    // 1. Arrange - 准备测试数据
    CardDTO cardDTO = new CardDTO();
    cardDTO.setCardNo("1234567890123456");
    cardDTO.setCardHolder("张三");
    cardDTO.setAmount(10000);
    
    CardDTO expectedCard = new CardDTO();
    expectedCard.setId(1001);
    expectedCard.setCardNo("1234567890123456");
    expectedCard.setUserId("user_001");
    
    // 2. Expect - 预期行为
    when(service.addCard(cardDTO)).thenReturn(expectedCard);
    when(cardManager.validate(cardDTO)).thenReturn(true);
    
    // 3. Act - 执行测试
    CardDTO result = service.addCard(cardDTO);
    
    // 4. Assert - 验证结果
    assertNotNull(result);
    assertEquals("1234567890123456", result.getCardNo());
    assertEquals("user_001", result.getUserId());
    verify(service, times(1)).addCard(cardDTO);
}
```

---

### **模板 2: 异常路径测试**

```java
@Test
public void testAddCard_Fail_InvalidCardNumber() throws Exception {
    // 1. Arrange - 准备异常数据
    CardDTO cardDTO = new CardDTO();
    cardDTO.setCardNo("12345"); // 无效卡号（长度不足）
    cardDTO.setCardHolder("张三");
    cardDTO.setAmount(10000);
    
    // 2. Expect - 预期抛出异常
    doThrow(new CardValidationException("卡号格式错误"))
        .when(cardManager).validate(cardDTO);
    
    // 3. Act & Assert - 验证异常抛出
    try {
        service.addCard(cardDTO);
        fail("Should throw CardValidationException");
    } catch (CardValidationException e) {
        assertEquals("卡号格式错误", e.getMessage());
    }
}
```

---

### **模板 3: 边界条件测试**

```java
@Test
public void testAddCard_Boundary_EmptyParameters() throws Exception {
    // 1. Arrange - 边界数据
    CardDTO cardDTO = new CardDTO();
    cardDTO.setCardNo(""); // 空卡号
    cardDTO.setCardHolder(""); // 空持卡人
    cardDTO.setAmount(0);
    
    // 2. Expect - 预期行为
    when(cardManager.validate(cardDTO)).thenReturn(false);
    
    // 3. Act & Assert
    try {
        service.addCard(cardDTO);
        fail("Should throw InvalidCardException");
    } catch (InvalidCardException e) {
        assertNotNull(e);
    }
    
    // 4. Verify - 验证没有被调用
    verify(service, never()).addCard(any());
}
```

---

### **模板 4: 数据提供者（多场景测试）**

```java
@DataProvider(name = "cardData")
public Object[][] provideCardData() {
    return new Object[][] {
        {new CardDTO("1234567890123456", "A"), 10000, true},
        {new CardDTO("12345", "B"), 5000, false},  // 卡号过短
        {new CardDTO("12345678901234567890", "C"), 0, false},  // 金额为 0
        {new CardDTO("1234567890123456", null), 10000, false},  // 持卡人 null
    };
}

@Test(dataProvider = "cardData")
public void testAddCard_DataProvider(CardDTO input, int amount, boolean expectSuccess) {
    CardDTO card = new CardDTO();
    card.setCardNo(input.getCardNo());
    card.setCardHolder(input.getCardHolder());
    card.setAmount(amount);
    
    if (expectSuccess) {
        when(service.addCard(card)).thenReturn(new CardDTO());
        CardDTO result = service.addCard(card);
        assertNotNull(result);
    } else {
        doThrow(new CardValidationException("测试失败"))
            .when(cardManager).validate(card);
        
        assertThrows(CardValidationException.class, () -> {
            service.addCard(card);
        });
    }
}
```

---

## 🎨 测试命名规范

### **推荐命名格式**

```java
// 格式：test_<方法名>_<场景>_<预期结果>
testGetCardInfo_Success              // 正常路径
testGetCardInfo_NotFound             // 查找失败
testGetCardInfo_InvalidCardNumber    // 卡号无效
testAddCard_WithValidData            // 添加成功
testAddCard_WithInvalidData          // 添加失败
testUpdateCard_ModifyAmount          // 修改金额
testUpdateCard_ModifyHolder          // 修改持卡人
```

---

## 📊 覆盖率要求

基于这个测试文件的最佳实践：

### **必需覆盖的场景**

1. ✅ 正常路径（Happy Path）
   - `testAddCard_Success`
   - `testGetCardInfo_Success`

2. ✅ **异常路径**
   - `testAddCard_IsNull`
   - `testAddCard_TooShort`
   - `testAddCard_Duplicate`

3. ✅ **边界条件**
   - `testAddCard_KindMaxValue`
   - `testAddCard_KindMinValue`
   - `testAddCard_ExtremeLength`

4. ✅ **数据提供者（可选但推荐）**
   - 多个合法数据
   - 多组非法数据

---

## 🔍 测试断言规范

### **推荐断言方法**

```java
// ✅ 推荐
assertNotNull(result);
assertEquals(expected, actual);
assertTrue(condition);
assertFalse(condition);
assertNull(value);

// ❌ 不推荐
assert(result != null);
assertEquals(actual, expected);  // 顺序反了，预期应该放前面
```

---

## 📝 测试日志记录

```java
@Test
public void testAddCard_withLogging() {
    // 记录测试开始
    logger.info("开始测试：testAddCard");
    
    CardDTO cardDTO = createTestCard();
    logger.debug("输入卡片：{}", cardDTO);
    
    try {
        CardDTO result = service.addCard(cardDTO);
        logger.debug("输出结果：{}", result);
        
        assertNotNull(result);
        logger.info("测试通过 ✅");
    } catch (Exception e) {
        logger.error("测试失败 ❌: {}", e.getMessage());
        throw e;
    }
}
```

---

## 💡 TDD 流程：Java 版本

### **扩展示 TDD 中的 TDD 执行器**

```python
# tdd-toolkit/run-java-test.py
"""
执行 Java TDD 测试的包装器
"""
import subprocess
from pathlib import Path

def run_java_tdd_test(test_file: str, project_root: str = "."):
    """
    运行 Java 单元测试
    
    参数:
        test_file: 测试文件路径（相对或绝对）
        project_root: Maven/Gradle 项目根目录
    
    返回:
        dict: 测试结果
    """
    # 查找测试文件
    test_path = Path(project_root) / test_file
    
    if not test_path.exists():
        return {"success": False, "error": "Test file not found"}
    
    # 尝试用 Maven 运行测试
    cmd = [
        "mvn", "test",
        f"-Dtest={test_path.stem}",
        "-Dmaven.test.failure.ignore=false"
    ]
    
    result = subprocess.run(
        cmd,
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=120  # Java 启动较慢
    )
    
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode
    }
```

然后你调用：

```bash
python run-java-tdd-test.py tests/java/CardManagementServiceUnitTest.java
```

---

## 📦 整合到你的 TDD Pipeline

在 `tdd-executor` 根目录创建：

```
tdd-executor/
├── examples/
│   └── java-tdd-example.md  # 本文件
│   └── tdd/
│       └── java/
│           ├── CardManagementServiceUnitTest.java  # 示例
│           └── test_runner.py  # Java 测试执行器
```

---

## 🚀 使用方式

### **方式 1: 直接看示例**

```bash
# 阅读示例
cat tdd-toolkit/examples/java-tdd-example.md

# 或使用 Claude Code 查看
claude code --path tdd-toolkit/examples/java-tdd-example.md --prompt "阅读并理解这个 Java TDD 示例"
```

### **方式 2: 让 Claude 生成类似测试**

```bash
claude code --path tdd-toolkit/ --prompt "参考 java-tdd-example.md 的规范，为我生成测试"
```

### **方式 3: 整理到你的项目**

```bash
# 复制示例到实际项目
cp tdd-toolkit/examples/java-tdd-example.md /Users/dylan/IdeaProjects/pcreditagreement/docs/TDD_EXAMPLE.md

# 更新你的测试文件
cp tdd-toolkit/examples/tdd/java/CardManagementServiceUnitTest.java /path/to/your/test/
```

---

## ✅ 验证清单

填写测试文件时，确保：

- [ ] ✅ 所有测试名称符合规范
- [ ] ✅ 正常路径有测试
- [ ] ✅ 异常路径有测试
- [ ] ✅ 边界条件有测试
- [ ] ✅ 断言使用推荐风格
- [ ] ✅ 有日志记录（可选）
- [ ] ✅ 测试可独立运行
- [ ] ✅ 测试覆盖率 > 80%

---

**基于原始文件：`CardManagementServiceUnitTest.java`**  
**位置：** `/Users/dylan/IdeaProjects/pcreditagreement/app/test/src/test/java/com/alipay/pcreditagreement/testng/test/unit/card/`  
**补充日期：** 2026-03-13
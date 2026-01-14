# 项目GitLab CI/CD流程建立计划（最终版）

## 1. 概述
基于项目现有配置和用户反馈，设计一个完整的GitLab CI/CD流程，实现代码质量检查、多环境测试、文档构建和包发布到本地PyPI服务器的自动化。

## 2. 技术栈
- **CI/CD平台**: GitLab CI/CD
- **依赖管理**: Poetry
- **代码质量**: Ruff (linting + formatting)
- **测试框架**: pytest
- **文档工具**: Sphinx
- **Python版本**: 3.11
- **测试环境**: Windows + Linux
- **PyPI服务器**: 本地PyPI服务器 (http://172.20.61.88:8080/simple/)

## 3. 分支开发策略
1. 从`main`分支创建功能分支（如`feature/v2`）
2. 在功能分支上进行开发和测试
3. 开发完成后，提交MR将功能分支合并到`main`
4. 合并到`main`分支后，自动触发完整的CI/CD流程
5. 确认所有检查通过后，创建Release触发发布流程

## 4. GitLab CI/CD配置设计

### 4.1 配置文件结构
创建`.gitlab-ci.yml`文件，包含以下结构：
- **stages**: 定义CI/CD流程的阶段
- **variables**: 定义全局变量，包括本地PyPI服务器配置
- **jobs**: 定义各个阶段的具体任务

### 4.2 阶段定义
```yaml
stages:
  - code_quality
  - test
  - build_docs
  - publish
```

### 4.3 全局变量配置
```yaml
variables:
  PYTHON_VERSION: "3.11"
  POETRY_VERSION: "1.8.0"
  SPHINXOPTS: "-W"
  LOCAL_PYPI_URL: "http://172.20.61.88:8080/simple/"  # 用户指定的URL
  LOCAL_PYPI_REPOSITORY: "local"
```

### 4.4 代码质量检查任务
```yaml
code_quality:
  stage: code_quality
  image: python:3.11-slim
  tags:
    - linux
  script:
    - pip install poetry==$POETRY_VERSION
    - poetry config repositories.$LOCAL_PYPI_REPOSITORY $LOCAL_PYPI_URL
    - poetry install
    - poetry run ruff check .
    - poetry run ruff format --check .
  artifacts:
    when: always
    paths:
      - .ruff_cache/
  except:
    - tags
```

### 4.5 多环境测试任务

#### 4.5.1 Linux环境测试
```yaml
test_linux:
  stage: test
  image: python:3.11-slim
  tags:
    - linux
  script:
    - pip install poetry==$POETRY_VERSION
    - poetry config repositories.$LOCAL_PYPI_REPOSITORY $LOCAL_PYPI_URL
    - poetry install
    - poetry run pytest --verbose
  artifacts:
    when: always
    paths:
      - .pytest_cache/
  except:
    - tags
```

#### 4.5.2 Windows环境测试
```yaml
test_windows:
  stage: test
  tags:
    - windows
  script:
    - python -m pip install poetry==$POETRY_VERSION
    - poetry config repositories.$LOCAL_PYPI_REPOSITORY $LOCAL_PYPI_URL
    - poetry install
    - poetry run pytest --verbose
  artifacts:
    when: always
    paths:
      - .pytest_cache/
  except:
    - tags
```

### 4.6 文档构建任务
```yaml
build_docs:
  stage: build_docs
  image: python:3.11-slim
  tags:
    - linux
  script:
    - pip install poetry==$POETRY_VERSION
    - poetry config repositories.$LOCAL_PYPI_REPOSITORY $LOCAL_PYPI_URL
    - poetry install
    - sphinx-build $SPHINXOPTS -b html docs/source docs/build/html
  artifacts:
    paths:
      - docs/build/html/
  except:
    - tags
```

### 4.7 包构建与发布任务
```yaml
build_package:
  stage: publish
  image: python:3.11-slim
  tags:
    - linux
  script:
    - pip install poetry==$POETRY_VERSION
    - poetry config repositories.$LOCAL_PYPI_REPOSITORY $LOCAL_PYPI_URL
    - poetry install
    - poetry build
  artifacts:
    paths:
      - dist/
  only:
    - tags

publish_to_local_pypi:
  stage: publish
  image: python:3.11-slim
  tags:
    - linux
  script:
    - pip install poetry==$POETRY_VERSION
    - poetry config repositories.$LOCAL_PYPI_REPOSITORY $LOCAL_PYPI_URL
    - poetry publish --repository $LOCAL_PYPI_REPOSITORY --username $LOCAL_PYPI_USERNAME --password $LOCAL_PYPI_PASSWORD
  dependencies:
    - build_package
  only:
    - tags
```

## 5. Runner配置
在GitLab项目中配置以下Runner：

### 5.1 Linux Runner
- 标签: `linux`
- 执行器: `docker` 或 `shell`
- 配置: 支持Python 3.11，能够访问本地PyPI服务器

### 5.2 Windows Runner
- 标签: `windows`
- 执行器: `shell`
- 配置: 已安装Python 3.11和Git，能够访问本地PyPI服务器

## 6. CI/CD变量配置
在GitLab项目的Settings > CI/CD > Variables中配置以下变量：

### 6.1 常规变量
- `PYTHON_VERSION`: "3.11"
- `POETRY_VERSION`: "1.8.0"
- `LOCAL_PYPI_URL`: "http://172.20.61.88:8080/simple/"  # 用户指定的URL
- `LOCAL_PYPI_REPOSITORY`: "local"

### 6.2 保护变量（Secret）
- `LOCAL_PYPI_USERNAME`: 本地PyPI服务器用户名（保护+掩码）
- `LOCAL_PYPI_PASSWORD`: 本地PyPI服务器密码（保护+掩码）

## 7. 分支保护规则
在GitLab项目的Settings > Repository > Protected branches中配置：

### 7.1 main分支保护
- 允许合并: 维护者
- 允许推送: 无（只能通过MR合并）
- 要求通过CI/CD管道: 启用
- 要求代码审查: 启用

## 8. 预期效果
- 每次推送代码或提交MR时，自动运行代码质量检查和多环境测试
- 确保代码符合项目的质量标准
- 支持Windows和Linux环境的测试
- 自动构建文档，确保文档质量
- 发布新版本时自动构建并发布到本地PyPI服务器

## 9. 实施步骤
1. 创建`.gitlab-ci.yml`文件
2. 配置GitLab Runner，确保能够访问本地PyPI服务器
3. 配置CI/CD变量，包括本地PyPI服务器的认证信息
4. 配置分支保护规则
5. 测试CI/CD流程运行
6. 根据实际运行结果调整配置
7. 完善文档，说明CI/CD流程的使用方法和维护指南

## 10. 后续优化建议
- 添加Python 3.12版本测试
- 实现部署到测试环境的自动化
- 添加性能测试和安全扫描
- 集成代码审查工具
- 实现增量测试，提高CI/CD运行效率
- 配置PyPI服务器的HTTPS访问（如果需要）

## 11. 完整配置文件
```yaml
# .gitlab-ci.yml

stages:
  - code_quality
  - test
  - build_docs
  - publish

variables:
  PYTHON_VERSION: "3.11"
  POETRY_VERSION: "1.8.0"
  SPHINXOPTS: "-W"
  LOCAL_PYPI_URL: "http://172.20.61.88:8080/simple/"  # 用户指定的URL
  LOCAL_PYPI_REPOSITORY: "local"

code_quality:
  stage: code_quality
  image: python:3.11-slim
  tags:
    - linux
  script:
    - pip install poetry==$POETRY_VERSION
    - poetry config repositories.$LOCAL_PYPI_REPOSITORY $LOCAL_PYPI_URL
    - poetry install
    - poetry run ruff check .
    - poetry run ruff format --check .
  artifacts:
    when: always
    paths:
      - .ruff_cache/
  except:
    - tags

test_linux:
  stage: test
  image: python:3.11-slim
  tags:
    - linux
  script:
    - pip install poetry==$POETRY_VERSION
    - poetry config repositories.$LOCAL_PYPI_REPOSITORY $LOCAL_PYPI_URL
    - poetry install
    - poetry run pytest --verbose
  artifacts:
    when: always
    paths:
      - .pytest_cache/
  except:
    - tags

test_windows:
  stage: test
  tags:
    - windows
  script:
    - python -m pip install poetry==$POETRY_VERSION
    - poetry config repositories.$LOCAL_PYPI_REPOSITORY $LOCAL_PYPI_URL
    - poetry install
    - poetry run pytest --verbose
  artifacts:
    when: always
    paths:
      - .pytest_cache/
  except:
    - tags

build_docs:
  stage: build_docs
  image: python:3.11-slim
  tags:
    - linux
  script:
    - pip install poetry==$POETRY_VERSION
    - poetry config repositories.$LOCAL_PYPI_REPOSITORY $LOCAL_PYPI_URL
    - poetry install
    - sphinx-build $SPHINXOPTS -b html docs/source docs/build/html
  artifacts:
    paths:
      - docs/build/html/
  except:
    - tags

build_package:
  stage: publish
  image: python:3.11-slim
  tags:
    - linux
  script:
    - pip install poetry==$POETRY_VERSION
    - poetry config repositories.$LOCAL_PYPI_REPOSITORY $LOCAL_PYPI_URL
    - poetry install
    - poetry build
  artifacts:
    paths:
      - dist/
  only:
    - tags

publish_to_local_pypi:
  stage: publish
  image: python:3.11-slim
  tags:
    - linux
  script:
    - pip install poetry==$POETRY_VERSION
    - poetry config repositories.$LOCAL_PYPI_REPOSITORY $LOCAL_PYPI_URL
    - poetry publish --repository $LOCAL_PYPI_REPOSITORY --username $LOCAL_PYPI_USERNAME --password $LOCAL_PYPI_PASSWORD
  dependencies:
    - build_package
  only:
    - tags
```
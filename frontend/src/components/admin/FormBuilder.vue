const userFormSchema = [
  {
    key: 'name',
    label: '姓名',
    type: 'input',
    placeholder: '请输入姓名',
    rules: [{ required: true, message: '请填写姓名' }]
  },
  {
    key: 'email',
    label: '邮箱',
    type: 'input',
    placeholder: '请输入邮箱',
    componentProps: { type: 'email' },
    rules: [
      { required: true, message: '请填写邮箱' },
      { pattern: /^\S+@\S+\.\S+$/, message: '邮箱格式不正确' }
    ]
  },
  {
    key: 'age',
    label: '年龄',
    type: 'number',
    placeholder: '请输入年龄',
    rules: [{ validator: (val) => val >= 0 && val <= 120, message: '年龄必须在0-120之间' }]
  },
  {
    key: 'status',
    label: '状态',
    type: 'select', // Note: This maps to picker, requires different handling internally
    options: [
      { label: '启用', value: 'active' },
      { label: '禁用', value: 'inactive' }
    ],
    rules: [{ required: true, message: '请选择状态' }]
  },
  {
    key: 'bio',
    label: '简介',
    type: 'textarea',
    rows: 3,
    placeholder: '请输入个人简介'
  }
];
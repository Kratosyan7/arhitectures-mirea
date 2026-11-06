	.file	"replspace.c"
	.option pic
	.attribute arch, "rv64i2p1_m2p0_a2p1_f2p2_d2p2_c2p0_zicsr2p0_zifencei2p0"
	.attribute unaligned_access, 0
	.attribute stack_align, 16
	.text
	.align	1
	.globl	my_replspace
	.type	my_replspace, @function
my_replspace:
.LFB23:
	.cfi_startproc
	mv	a4,a1
	li	a3,32
	li	a2,95
.L5:
	lbu	a5,0(a0)
	beq	a5,a3,.L7
	sb	a5,0(a4)
	addi	a0,a0,1
	addi	a4,a4,1
	bne	a5,zero,.L5
	subw	a0,a4,a1
	ret
.L7:
	addi	a4,a4,1
	addi	a0,a0,1
	sb	a2,-1(a4)
	j	.L5
	.cfi_endproc
.LFE23:
	.size	my_replspace, .-my_replspace
	.section	.rodata.str1.8,"aMS",@progbits,1
	.align	3
.LC0:
	.string	"Input:  %s\nOutput: %s\n"
	.section	.text.startup,"ax",@progbits
	.align	1
	.globl	main
	.type	main, @function
main:
.LFB24:
	.cfi_startproc
	addi	sp,sp,-16
	.cfi_def_cfa_offset 16
	ld	a2,.LANCHOR1
	sd	ra,8(sp)
	.cfi_offset 1, -8
	mv	a3,a2
	lla	a4,.LANCHOR0
	li	a1,32
	li	a0,95
.L12:
	lbu	a5,0(a3)
	beq	a5,a1,.L14
	sb	a5,0(a4)
	addi	a3,a3,1
	addi	a4,a4,1
	bne	a5,zero,.L12
	lla	a3,.LANCHOR0
	lla	a1,.LC0
	li	a0,2
	call	__printf_chk@plt
	ld	ra,8(sp)
	.cfi_remember_state
	.cfi_restore 1
	li	a0,0
	addi	sp,sp,16
	.cfi_def_cfa_offset 0
	jr	ra
.L14:
	.cfi_restore_state
	addi	a4,a4,1
	addi	a3,a3,1
	sb	a0,-1(a4)
	j	.L12
	.cfi_endproc
.LFE24:
	.size	main, .-main
	.globl	outStr
	.globl	tstStr
	.section	.rodata.str1.8
	.align	3
.LC1:
	.string	"Lab Work 5"
	.bss
	.align	3
	.set	.LANCHOR0,. + 0
	.type	outStr, @object
	.size	outStr, 64
outStr:
	.zero	64
	.section	.data.rel.local,"aw"
	.align	3
	.set	.LANCHOR1,. + 0
	.type	tstStr, @object
	.size	tstStr, 8
tstStr:
	.dword	.LC1
	.ident	"GCC: (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0"
	.section	.note.GNU-stack,"",@progbits
